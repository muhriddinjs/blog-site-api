from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional
from math import ceil
import uuid
from slugify import slugify

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.article import Article, ArticleCategory, ArticleStatus
from app.models.user import User
from app.schemas.article import (
    ArticleCreate, ArticleUpdate, ArticleResponse,
    ArticleListResponse, PaginatedArticles
)
from app.utils.file_upload import save_upload_file, delete_file

router = APIRouter()

# ─── PUBLIC ENDPOINTS ────────────────────────────────────────────────────────

public_router = APIRouter(prefix="/articles", tags=["Articles - Public"])


@public_router.get("", response_model=PaginatedArticles)
async def get_published_articles(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    category: Optional[ArticleCategory] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Nashr qilingan maqolalar ro'yxati"""
    query = select(Article).where(Article.status == ArticleStatus.published)

    if category:
        query = query.where(Article.category == category)
    if search:
        query = query.where(
            or_(
                Article.title.ilike(f"%{search}%"),
                Article.summary.ilike(f"%{search}%"),
            )
        )

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    query = query.order_by(Article.published_at.desc())
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    articles = result.scalars().all()

    return PaginatedArticles(
        items=articles,
        total=total,
        page=page,
        size=size,
        pages=ceil(total / size) if total else 0
    )


@public_router.get("/{slug}", response_model=ArticleResponse)
async def get_article_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    """Slug bo'yicha maqolani ko'rish (view count oshadi)"""
    result = await db.execute(
        select(Article).where(
            Article.slug == slug,
            Article.status == ArticleStatus.published
        )
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Maqola topilmadi")

    article.views += 1
    await db.commit()
    await db.refresh(article)
    return article


# ─── ADMIN ENDPOINTS ──────────────────────────────────────────────────────────

admin_router = APIRouter(prefix="/admin/articles", tags=["Articles - Admin"])


@admin_router.get("", response_model=PaginatedArticles)
async def admin_get_articles(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    category: Optional[ArticleCategory] = None,
    status: Optional[ArticleStatus] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    query = select(Article)
    if category:
        query = query.where(Article.category == category)
    if status:
        query = query.where(Article.status == status)
    if search:
        query = query.where(
            or_(Article.title.ilike(f"%{search}%"), Article.summary.ilike(f"%{search}%"))
        )

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    query = query.order_by(Article.created_at.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    articles = result.scalars().all()

    return PaginatedArticles(
        items=articles, total=total, page=page, size=size,
        pages=ceil(total / size) if total else 0
    )


@admin_router.get("/{article_id}", response_model=ArticleResponse)
async def admin_get_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Maqola topilmadi")
    return article


@admin_router.post("", response_model=ArticleResponse, status_code=201)
async def admin_create_article(
    data: ArticleCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    # Slug auto-generate
    slug = data.slug or slugify(data.title)

    # Slug noyobligini tekshirish
    existing = await db.execute(select(Article).where(Article.slug == slug))
    if existing.scalar_one_or_none():
        slug = f"{slug}-{uuid.uuid4().hex[:8]}"

    article = Article(**data.model_dump(exclude={"slug"}), slug=slug)
    db.add(article)
    await db.commit()
    await db.refresh(article)
    return article


@admin_router.put("/{article_id}", response_model=ArticleResponse)
async def admin_update_article(
    article_id: int,
    data: ArticleUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Maqola topilmadi")

    update_data = data.model_dump(exclude_unset=True)
    if "title" in update_data and "slug" not in update_data:
        update_data["slug"] = slugify(update_data["title"])

    for key, value in update_data.items():
        setattr(article, key, value)

    await db.commit()
    await db.refresh(article)
    return article


@admin_router.delete("/{article_id}", status_code=204)
async def admin_delete_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Maqola topilmadi")

    # Agar fayl bo'lsa o'chirish
    if article.image and article.image.startswith("/uploads"):
        delete_file(article.image)

    await db.delete(article)
    await db.commit()


@admin_router.post("/{article_id}/upload-image", response_model=dict)
async def admin_upload_article_image(
    article_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Maqola topilmadi")

    # Eski rasmni o'chirish
    if article.image and article.image.startswith("/uploads"):
        delete_file(article.image)

    url = await save_upload_file(file, "articles")
    article.image = url
    await db.commit()
    return {"image_url": url}
