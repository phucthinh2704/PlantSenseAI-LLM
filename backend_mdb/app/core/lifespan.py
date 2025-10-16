# app/core/lifespan.py

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from diskcache import Cache
from dotenv import load_dotenv
from app.models.user import create_admin_user
from app.core.database import create_indexes, client

load_dotenv()

# Khởi tạo các biến toàn cục để lưu trữ model và lịch sử chat
models_cache = {}
conversation_histories = Cache("cache/chat_histories")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Đang tải các model...")
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    models_cache["embedding_model"] = SentenceTransformer(os.getenv("EMBEDDING_MODEL_NAME", "intfloat/multilingual-e5-large"))
    models_cache["qdrant_client"] = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
    )
    models_cache["llm_rag"] = genai.GenerativeModel("gemini-2.5-pro")
    models_cache["llm_fast"] = genai.GenerativeModel("gemini-2.5-flash")
    
    logging.info("Tải model thành công!")
    
    # Startup
    print("Ứng dụng đang khởi động...")
    await create_indexes()  # tạo index bất đồng bộ

    await create_admin_user()
    print("Các chỉ mục và admin đã được tạo thành công.")
    
    yield
    print("Đang đóng kết nối MongoDB...")
    client.close()
    print("Kết nối đã được đóng.")
    # Dọn dẹp khi tắt server
    models_cache.clear()
    conversation_histories.close()