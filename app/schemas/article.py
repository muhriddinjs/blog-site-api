from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.article import ArticleCategory, ArticleStatus


class ArticleBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    slug: Optional[str] = Field(None, max_length=300)
    summary: str = Field(..., min_length=10)
    category: ArticleCategory = ArticleCategory.other
    status: ArticleStatus = ArticleStatus.draft
    read_time: int = Field(5, ge=1, le=120)
    image: Optional[str] = None
    content: str = Field(..., min_length=10)
    seo_title: Optional[str] = Field(None, max_length=255)
    seo_description: Optional[str] = None
    keywords: Optional[str] = Field(None, max_length=500)


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    slug: Optional[str] = Field(None, max_length=300)
    summary: Optional[str] = None
    category: Optional[ArticleCategory] = None
    status: Optional[ArticleStatus] = None
    read_time: Optional[int] = Field(None, ge=1, le=120)
    image: Optional[str] = None
    content: Optional[str] = None
    seo_title: Optional[str] = Field(None, max_length=255)
    seo_description: Optional[str] = None
    keywords: Optional[str] = None


class ArticleResponse(ArticleBase):
    id: int
    views: int
    published_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ArticleListResponse(BaseModel):
    id: int
    title: str
    slug: str
    summary: str
    category: ArticleCategory
    status: ArticleStatus
    read_time: int
    image: Optional[str]
    published_at: datetime
    views: int

    model_config = {"from_attributes": True}


class PaginatedArticles(BaseModel):
    items: List[ArticleResponse]
    total: int
    page: int
    size: int
    pages: int
