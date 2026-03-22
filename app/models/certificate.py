from sqlalchemy import String, Text, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy import String as SA_String
from app.core.database import Base
from datetime import datetime
import enum


class CertificateType(str, enum.Enum):
    certificate = "certificate"
    diploma = "diploma"
    course = "course"
    badge = "badge"


class Certificate(Base):
    __tablename__ = "certificates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    issuer: Mapped[str] = mapped_column(String(255), nullable=False)
    certificate_type: Mapped[CertificateType] = mapped_column(
        Enum(CertificateType), nullable=False, default=CertificateType.certificate
    )
    skills: Mapped[list[str]] = mapped_column(
        PG_ARRAY(SA_String), nullable=False, default=list
    )
    image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    credential_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    issued_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expiry_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<Certificate {self.name}>"
