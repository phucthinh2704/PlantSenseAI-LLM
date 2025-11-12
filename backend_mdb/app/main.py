from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    chat_router,
    admin_router,
    user_router,
)
from app.core.lifespan import lifespan


app = FastAPI(
    title="PlantSense API",
    description="API cho chatbot luận văn tốt nghiệp",
    lifespan=lifespan,
    version="1.0.0",
)

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
app.include_router(chat_router.router, prefix="/chat", tags=["Chat"])
app.include_router(admin_router.router, prefix="/admin", tags=["Admin"])
app.include_router(user_router.router, prefix="/users", tags=["Users"])

# py -m app.main
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
