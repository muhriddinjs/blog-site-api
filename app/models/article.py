from sqlalchemy import String, Text, DateTime, Enum, Integer, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from datetime import datetime
import enum


class ArticleCategory(str, enum.Enum):
    design = "design"
    performance = "performance"
    backend = "backend"
    frontend = "frontend"
    devops = "devops"
    mobile = "mobile"
    other = "other"


class ArticleStatus(str, enum.Enum):
    draft = "draft"
    published = "published"


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), unique=True, index=True, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[ArticleCategory] = mapped_column(
        Enum(ArticleCategory), nullable=False, default=ArticleCategory.other
    )
    status: Mapped[ArticleStatus] = mapped_column(
        Enum(ArticleStatus), nullable=False, default=ArticleStatus.draft
    )
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    read_time: Mapped[int] = mapped_column(Integer, default=5, comment="minutlarda")
    image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    seo_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    seo_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    keywords: Mapped[str | None] = mapped_column(String(500), nullable=True)
    views: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<Article {self.title}>"
