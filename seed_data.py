import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123456"

async def seed():
    async with httpx.AsyncClient() as client:
        # 1. Login
        print("Logging in...")
        login_resp = await client.post(
            f"{BASE_URL}/auth/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if login_resp.status_code != 200:
            print(f"Login failed: {login_resp.text}")
            return
        
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Login successful.")

        # 2. Add 6 Articles
        articles = [
            {
                "title": f"FastAPI bilan Backend rivojlantirish {i}",
                "summary": f"Ushbu maqolada FastAPI yordamida zamonaviy backend tizimlarini yaratish haqida gaplashamiz. Qism {i}.",
                "content": f"To'liq kontent bu yerda. FastAPI juda tez va qulay framework hisoblanadi. {i*10} xil uslublar mavjud.",
                "category": "backend",
                "status": "published",
                "read_time": 5 + i
            } for i in range(1, 7)
        ]
        for art in articles:
            resp = await client.post(f"{BASE_URL}/admin/articles", json=art, headers=headers)
            print(f"Article '{art['title']}' created: {resp.status_code}")

        # 3. Add 4 Portfolios
        portfolios = [
            {
                "name": f"Project X-{i}",
                "category": "web" if i % 2 == 0 else "backend",
                "description": f"Bu loyiha juda foydali va qiziqarli. {i}-versiya.",
                "technologies": ["Python", "FastAPI", "React"],
                "tags": ["web", "api", "portfolio"],
                "is_featured": True if i == 1 else False,
                "order": i
            } for i in range(1, 5)
        ]
        for port in portfolios:
            resp = await client.post(f"{BASE_URL}/admin/portfolios", json=port, headers=headers)
            print(f"Portfolio '{port['name']}' created: {resp.status_code}")

        # 4. Add 4 Certificates
        certificates = [
            {
                "name": f"Python Advanced Certificate {i}",
                "issuer": "Coursera / Google",
                "certificate_type": "certificate",
                "skills": ["Python", "Algorithms", "Testing"],
                "credential_url": "https://example.com/cert"
            } for i in range(1, 5)
        ]
        for cert in certificates:
            resp = await client.post(f"{BASE_URL}/admin/certificates", json=cert, headers=headers)
            print(f"Certificate '{cert['name']}' created: {resp.status_code}")

if __name__ == "__main__":
    asyncio.run(seed())
