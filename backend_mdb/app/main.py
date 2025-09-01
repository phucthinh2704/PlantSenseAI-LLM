from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

import os
from app.router import plant_router, auth_router
from app.core.database import create_indexes, client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Ứng dụng đang khởi động...")
    await create_indexes()  # tạo index bất đồng bộ
    print("Các chỉ mục đã được tạo thành công.")
    yield  # đây là điểm ứng dụng "đang chạy"
    # Shutdown
    print("Đang đóng kết nối MongoDB...")
    client.close()
    print("Kết nối đã được đóng.")

app = FastAPI(title="PlantSense API", lifespan=lifespan)

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký router
app.include_router(plant_router.router, prefix="/plants", tags=["Plants"])
app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])

# py -m app.main
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)