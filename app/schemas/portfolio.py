from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from app.models.portfolio import PortfolioCategory


class PortfolioBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    category: PortfolioCategory = PortfolioCategory.other
    description: Optional[str] = None
    technologies: List[str] = []
    tags: List[str] = []
    live_url: Optional[str] = None
    github_url: Optional[str] = None
    image: Optional[str] = None
    is_featured: bool = False
    order: int = 0


class PortfolioCreate(PortfolioBase):
    pass


class PortfolioUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    category: Optional[PortfolioCategory] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    live_url: Optional[str] = None
    github_url: Optional[str] = None
    image: Optional[str] = None
    is_featured: Optional[bool] = None
    order: Optional[int] = None


class PortfolioResponse(PortfolioBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedPortfolios(BaseModel):
    items: List[PortfolioResponse]
    total: int
    page: int
    size: int
    pages: int
