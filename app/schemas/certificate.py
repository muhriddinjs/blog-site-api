from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.certificate import CertificateType


class CertificateBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    issuer: str = Field(..., min_length=2, max_length=255)
    certificate_type: CertificateType = CertificateType.certificate
    skills: List[str] = []
    image: Optional[str] = None
    credential_url: Optional[str] = None
    issued_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None


class CertificateCreate(CertificateBase):
    pass


class CertificateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    issuer: Optional[str] = Field(None, min_length=2, max_length=255)
    certificate_type: Optional[CertificateType] = None
    skills: Optional[List[str]] = None
    image: Optional[str] = None
    credential_url: Optional[str] = None
    issued_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None


class CertificateResponse(CertificateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedCertificates(BaseModel):
    items: List[CertificateResponse]
    total: int
    page: int
    size: int
    pages: int
