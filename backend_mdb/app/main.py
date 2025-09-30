from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.user import create_admin_user
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

import os
from app.router import (
    plant_router,
    auth_router,
    cultivation_router,
    disease_router,
    disease_stage_router,
    insert_router,
    conversation_router,
    qdrant_router,
)
from app.core.database import create_indexes, client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Ứng dụng đang khởi động...")
    await create_indexes()  # tạo index bất đồng bộ
    print("Các chỉ mục đã được tạo thành công.")

    await create_admin_user()
    print("Các chỉ mục và admin đã được tạo thành công.")
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
app.include_router(disease_router.router, prefix="/diseases", tags=["Diseases"])
app.include_router(
    disease_stage_router.router, prefix="/disease-stages", tags=["Disease Stages"]
)
app.include_router(
    cultivation_router.router, prefix="/cultivation", tags=["Cultivation"]
)
app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.include_router(
    conversation_router.router, prefix="/conversations", tags=["Conversations"]
)
app.include_router(insert_router.router, prefix="/insert", tags=["Insert"])
app.include_router(qdrant_router.router, prefix="/qdrant", tags=["Search"])

# py -m app.main
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
