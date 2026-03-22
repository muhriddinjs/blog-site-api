# Portfolio Backend API

FastAPI + PostgreSQL asosida qurilgan to'liq portfolio backend.

## 📦 Loyiha tuzilmasi

```
portfolio-backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py          # Login, refresh, me
│   │       │   ├── articles.py      # Maqolalar (public + admin)
│   │       │   ├── portfolios.py    # Portfoliolar (public + admin)
│   │       │   └── certificates.py  # Sertifikatlar (public + admin)
│   │       └── router.py
│   ├── core/
│   │   ├── config.py       # Sozlamalar (.env)
│   │   ├── database.py     # DB ulanish
│   │   └── security.py     # JWT, bcrypt
│   ├── models/
│   │   ├── user.py
│   │   ├── article.py
│   │   ├── portfolio.py
│   │   └── certificate.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── article.py
│   │   ├── portfolio.py
│   │   └── certificate.py
│   ├── utils/
│   │   └── file_upload.py  # Rasm yuklash
│   └── main.py             # App entry point
├── alembic/                # DB migratsiyalar
├── uploads/                # Yuklangan rasmlar
├── .env.example
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## 🚀 Ishga tushirish

### 1. Virtual muhit va kutubxonalar

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. .env fayl yaratish

```bash
cp .env.example .env
# .env faylni o'z sozlamalaringizga moslang
```

### 3. PostgreSQL bazasini yaratish

```bash
psql -U postgres
CREATE DATABASE portfolio_db;
\q
```

### 4. Serverni ishga tushirish

```bash
uvicorn app.main:app --reload
```

Server avtomatik ravishda:
- Barcha jadvallarni yaratadi
- Birinchi admin foydalanuvchini yaratadi (`.env` dagi sozlamalar bilan)

### 5. Swagger UI

```
http://localhost:8000/docs
```

---

## 🐳 Docker bilan ishga tushirish

```bash
# .env faylni yarating
cp .env.example .env

# Docker Compose bilan ishga tushirish
docker-compose up -d

# Loglarni ko'rish
docker-compose logs -f api
```

---

## 🔐 API Endpointlar

### Auth
| Method | URL | Tavsif | Auth |
|--------|-----|--------|------|
| POST | `/api/v1/auth/login` | Admin login | ❌ |
| POST | `/api/v1/auth/refresh` | Token yangilash | ❌ |
| GET | `/api/v1/auth/me` | Joriy admin ma'lumoti | ✅ |

### Maqolalar (Public)
| Method | URL | Tavsif |
|--------|-----|--------|
| GET | `/api/v1/articles` | Nashr qilingan maqolalar |
| GET | `/api/v1/articles/{slug}` | Maqolani slug bo'yicha o'qish |

### Maqolalar (Admin)
| Method | URL | Tavsif |
|--------|-----|--------|
| GET | `/api/v1/admin/articles` | Barcha maqolalar |
| GET | `/api/v1/admin/articles/{id}` | Bitta maqola |
| POST | `/api/v1/admin/articles` | Maqola qo'shish |
| PUT | `/api/v1/admin/articles/{id}` | Maqolani tahrirlash |
| DELETE | `/api/v1/admin/articles/{id}` | Maqolani o'chirish |
| POST | `/api/v1/admin/articles/{id}/upload-image` | Rasm yuklash |

### Portfoliolar
| Method | URL | Auth |
|--------|-----|------|
| GET | `/api/v1/portfolios` | ❌ |
| GET | `/api/v1/portfolios/{id}` | ❌ |
| POST | `/api/v1/admin/portfolios` | ✅ |
| PUT | `/api/v1/admin/portfolios/{id}` | ✅ |
| DELETE | `/api/v1/admin/portfolios/{id}` | ✅ |
| POST | `/api/v1/admin/portfolios/{id}/upload-image` | ✅ |

### Sertifikatlar
| Method | URL | Auth |
|--------|-----|------|
| GET | `/api/v1/certificates` | ❌ |
| GET | `/api/v1/certificates/{id}` | ❌ |
| POST | `/api/v1/admin/certificates` | ✅ |
| PUT | `/api/v1/admin/certificates/{id}` | ✅ |
| DELETE | `/api/v1/admin/certificates/{id}` | ✅ |
| POST | `/api/v1/admin/certificates/{id}/upload-image` | ✅ |

---

## 🔑 Authentication

Login qilish:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123456"}'
```

Token bilan so'rov yuborish:
```bash
curl http://localhost:8000/api/v1/admin/articles \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📁 Rasm yuklash

Rasm yuklash (multipart/form-data):
```bash
curl -X POST http://localhost:8000/api/v1/admin/articles/1/upload-image \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/image.jpg"
```

Yoki maqola yaratishda `image` maydoniga URL berishingiz mumkin:
```json
{
  "image": "https://example.com/image.jpg"
}
```

---

## 🔍 Filter & Pagination

```
GET /api/v1/articles?page=1&size=10&category=backend&search=python
GET /api/v1/portfolios?category=fullstack&featured=true
GET /api/v1/certificates?certificate_type=sertifikat
```

---

## ⚙️ Muhit o'zgaruvchilari

| Variable | Tavsif | Default |
|----------|--------|---------|
| `DATABASE_URL` | PostgreSQL ulanish URL | - |
| `SECRET_KEY` | JWT secret kalit | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token muddati (daqiqa) | 60 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token muddati (kun) | 7 |
| `ADMIN_EMAIL` | Birinchi admin email | - |
| `ADMIN_PASSWORD` | Birinchi admin parol | - |
| `UPLOAD_DIR` | Rasm yuklash papkasi | uploads |
| `MAX_FILE_SIZE` | Max fayl hajmi (bayt) | 10485760 |
| `ALLOWED_ORIGINS` | CORS ruxsat etilgan domainlar | - |
