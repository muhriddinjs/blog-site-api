from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class About(Base):
    __tablename__ = "about_info"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, default=1)
    name: Mapped[str] = mapped_column(String(255), default="Sizning Ismingiz")
    title: Mapped[str] = mapped_column(String(255), default="Full Stack Developer")
    tagline: Mapped[str] = mapped_column(String(500), default="Innovatsiya va kreativlik")
    bio: Mapped[str] = mapped_column(Text, default="Men haqimda")
    stats: Mapped[list[dict]] = mapped_column(JSON, default=list)

    def __repr__(self):
        return f"<About {self.name}>"
