from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from math import ceil

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.portfolio import Portfolio, PortfolioCategory
from app.models.user import User
from app.schemas.portfolio import (
    PortfolioCreate, PortfolioUpdate, PortfolioResponse, PaginatedPortfolios
)
from app.utils.file_upload import save_upload_file, delete_file

router = APIRouter()

public_router = APIRouter(prefix="/portfolios", tags=["Portfolios - Public"])
admin_router = APIRouter(prefix="/admin/portfolios", tags=["Portfolios - Admin"])


# ─── PUBLIC ───────────────────────────────────────────────────────────────────

@public_router.get("", response_model=PaginatedPortfolios)
async def get_portfolios(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    category: Optional[PortfolioCategory] = None,
    featured: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Portfolio)
    if category:
        query = query.where(Portfolio.category == category)
    if featured is not None:
        query = query.where(Portfolio.is_featured == featured)

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    query = query.order_by(Portfolio.order.asc(), Portfolio.created_at.desc())
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)

    return PaginatedPortfolios(
        items=result.scalars().all(), total=total, page=page, size=size,
        pages=ceil(total / size) if total else 0
    )


@public_router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(portfolio_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio topilmadi")
    return portfolio


# ─── ADMIN ────────────────────────────────────────────────────────────────────

@admin_router.get("", response_model=PaginatedPortfolios)
async def admin_get_portfolios(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    category: Optional[PortfolioCategory] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    query = select(Portfolio)
    if category:
        query = query.where(Portfolio.category == category)

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    query = query.order_by(Portfolio.order.asc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)

    return PaginatedPortfolios(
        items=result.scalars().all(), total=total, page=page, size=size,
        pages=ceil(total / size) if total else 0
    )


@admin_router.post("", response_model=PortfolioResponse, status_code=201)
async def admin_create_portfolio(
    data: PortfolioCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    portfolio = Portfolio(**data.model_dump())
    db.add(portfolio)
    await db.commit()
    await db.refresh(portfolio)
    return portfolio


@admin_router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def admin_update_portfolio(
    portfolio_id: int,
    data: PortfolioUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio topilmadi")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(portfolio, key, value)

    await db.commit()
    await db.refresh(portfolio)
    return portfolio


@admin_router.delete("/{portfolio_id}", status_code=204)
async def admin_delete_portfolio(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio topilmadi")

    if portfolio.image and portfolio.image.startswith("/uploads"):
        delete_file(portfolio.image)

    await db.delete(portfolio)
    await db.commit()


@admin_router.post("/{portfolio_id}/upload-image", response_model=dict)
async def admin_upload_portfolio_image(
    portfolio_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio topilmadi")

    if portfolio.image and portfolio.image.startswith("/uploads"):
        delete_file(portfolio.image)

    url = await save_upload_file(file, "portfolios")
    portfolio.image = url
    await db.commit()
    return {"image_url": url}
