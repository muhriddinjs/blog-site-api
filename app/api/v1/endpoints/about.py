from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.user import User
from app.models.about import About
from app.schemas.about import AboutResponse, AboutUpdate

public_router = APIRouter(prefix="/about", tags=["About - Public"])
admin_router = APIRouter(prefix="/admin/about", tags=["About - Admin"])

@public_router.get("", response_model=AboutResponse)
async def get_about(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(About).where(About.id == 1))
    about = result.scalar_one_or_none()
    if not about:
        about = About(id=1, name="Sizning Ismingiz", title="Developer", tagline="", bio="", stats=[])
        db.add(about)
        await db.commit()
        await db.refresh(about)
    return about

@admin_router.get("", response_model=AboutResponse)
async def admin_get_about(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_admin)):
    result = await db.execute(select(About).where(About.id == 1))
    about = result.scalar_one_or_none()
    if not about:
        about = About(id=1, name="Sizning Ismingiz", title="Developer", tagline="", bio="", stats=[])
        db.add(about)
        await db.commit()
        await db.refresh(about)
    return about

@admin_router.put("", response_model=AboutResponse)
async def admin_update_about(data: AboutUpdate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_admin)):
    result = await db.execute(select(About).where(About.id == 1))
    about = result.scalar_one_or_none()
    
    if not about:
        about = About(id=1, **data.model_dump())
        db.add(about)
    else:
        # Convert stats dict list to JSON compatible list
        stats_list = [stat.model_dump() for stat in data.stats]
        about.name = data.name
        about.title = data.title
        about.tagline = data.tagline
        about.bio = data.bio
        about.stats = stats_list
        
    await db.commit()
    await db.refresh(about)
    return about
