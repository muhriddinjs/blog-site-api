from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
import os

from app.core.config import settings
from app.core.database import engine, AsyncSessionLocal, Base
from app.api.v1.router import api_router


async def create_tables():
    """Barcha jadvallarni yaratish"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_admin():
    """Birinchi admin foydalanuvchini yaratish"""
    from app.models.user import User
    from app.core.security import get_password_hash

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == settings.ADMIN_EMAIL))
        existing = result.scalar_one_or_none()

        if not existing:
            admin = User(
                username=settings.ADMIN_USERNAME,
                email=settings.ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                is_active=True,
                is_admin=True,
            )
            db.add(admin)
            await db.commit()
            print(f"✅ Admin yaratildi: {settings.ADMIN_EMAIL}")
        else:
            print(f"ℹ️  Admin allaqachon mavjud: {settings.ADMIN_EMAIL}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Server ishga tushmoqda...")
    await create_tables()
    await create_admin()

    # Upload papkalarini yaratish
    for folder in ["articles", "portfolios", "certificates"]:
        os.makedirs(f"{settings.UPLOAD_DIR}/{folder}", exist_ok=True)

    print("✅ Tayyor!")
    yield
    # Shutdown
    await engine.dispose()
    print("🛑 Server to'xtatildi")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Portfolio, Blog va Sertifikatlar uchun to'liq REST API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static fayllar (yuklangan rasmlar)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Router
app.include_router(api_router)


@app.get("/", tags=["Root"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running ✅",
    }


@app.get("/health", tags=["Root"])
async def health_check():
    return {"status": "ok"}
