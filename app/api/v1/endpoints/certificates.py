from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from math import ceil

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.certificate import Certificate, CertificateType
from app.models.user import User
from app.schemas.certificate import (
    CertificateCreate, CertificateUpdate, CertificateResponse, PaginatedCertificates
)
from app.utils.file_upload import save_upload_file, delete_file

public_router = APIRouter(prefix="/certificates", tags=["Certificates - Public"])
admin_router = APIRouter(prefix="/admin/certificates", tags=["Certificates - Admin"])


# ─── PUBLIC ───────────────────────────────────────────────────────────────────

@public_router.get("", response_model=PaginatedCertificates)
async def get_certificates(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    certificate_type: Optional[CertificateType] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Certificate)
    if certificate_type:
        query = query.where(Certificate.certificate_type == certificate_type)

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    query = query.order_by(Certificate.issued_date.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)

    return PaginatedCertificates(
        items=result.scalars().all(), total=total, page=page, size=size,
        pages=ceil(total / size) if total else 0
    )


@public_router.get("/{certificate_id}", response_model=CertificateResponse)
async def get_certificate(certificate_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Certificate).where(Certificate.id == certificate_id))
    cert = result.scalar_one_or_none()
    if not cert:
        raise HTTPException(status_code=404, detail="Sertifikat topilmadi")
    return cert


# ─── ADMIN ────────────────────────────────────────────────────────────────────

@admin_router.get("", response_model=PaginatedCertificates)
async def admin_get_certificates(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    total_result = await db.execute(select(func.count(Certificate.id)))
    total = total_result.scalar()

    result = await db.execute(
        select(Certificate).order_by(Certificate.created_at.desc())
        .offset((page - 1) * size).limit(size)
    )
    return PaginatedCertificates(
        items=result.scalars().all(), total=total, page=page, size=size,
        pages=ceil(total / size) if total else 0
    )


@admin_router.post("", response_model=CertificateResponse, status_code=201)
async def admin_create_certificate(
    data: CertificateCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    cert = Certificate(**data.model_dump())
    db.add(cert)
    await db.commit()
    await db.refresh(cert)
    return cert


@admin_router.put("/{certificate_id}", response_model=CertificateResponse)
async def admin_update_certificate(
    certificate_id: int,
    data: CertificateUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    result = await db.execute(select(Certificate).where(Certificate.id == certificate_id))
    cert = result.scalar_one_or_none()
    if not cert:
        raise HTTPException(status_code=404, detail="Sertifikat topilmadi")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(cert, key, value)

    await db.commit()
    await db.refresh(cert)
    return cert


@admin_router.delete("/{certificate_id}", status_code=204)
async def admin_delete_certificate(
    certificate_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    result = await db.execute(select(Certificate).where(Certificate.id == certificate_id))
    cert = result.scalar_one_or_none()
    if not cert:
        raise HTTPException(status_code=404, detail="Sertifikat topilmadi")

    if cert.image and cert.image.startswith("/uploads"):
        delete_file(cert.image)

    await db.delete(cert)
    await db.commit()


@admin_router.post("/{certificate_id}/upload-image", response_model=dict)
async def admin_upload_certificate_image(
    certificate_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    result = await db.execute(select(Certificate).where(Certificate.id == certificate_id))
    cert = result.scalar_one_or_none()
    if not cert:
        raise HTTPException(status_code=404, detail="Sertifikat topilmadi")

    if cert.image and cert.image.startswith("/uploads"):
        delete_file(cert.image)

    url = await save_upload_file(file, "certificates")
    cert.image = url
    await db.commit()
    return {"image_url": url}
