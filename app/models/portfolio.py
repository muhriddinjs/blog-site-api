from sqlalchemy import String, Text, DateTime, Enum, func, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy import String as SA_String
from app.core.database import Base
from datetime import datetime
import enum


class PortfolioCategory(str, enum.Enum):
    web = "web"
    mobile = "mobile"
    design = "design"
    backend = "backend"
    fullstack = "fullstack"
    other = "other"


class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[PortfolioCategory] = mapped_column(
        Enum(PortfolioCategory), nullable=False, default=PortfolioCategory.other
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    technologies: Mapped[list[str]] = mapped_column(
        PG_ARRAY(SA_String), nullable=False, default=list
    )
    tags: Mapped[list[str]] = mapped_column(
        PG_ARRAY(SA_String), nullable=False, default=list
    )
    live_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_featured: Mapped[bool] = mapped_column(default=False)
    order: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<Portfolio {self.name}>"
