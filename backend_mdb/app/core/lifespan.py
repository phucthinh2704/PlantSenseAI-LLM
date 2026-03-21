# import os
# from contextlib import asynccontextmanager
# from fastapi import FastAPI
# from qdrant_client import QdrantClient
# from sentence_transformers import SentenceTransformer
# import google.generativeai as genai
# from diskcache import Cache
# from dotenv import load_dotenv
# from app.models.user import create_admin_user
# from app.core.database import create_indexes, client

# load_dotenv()

# # Khởi tạo các biến toàn cục để lưu trữ model và lịch sử chat
# models_cache = {}
# conversation_histories = Cache("cache/chat_histories")

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

#     # models_cache["embedding_model"] = SentenceTransformer(os.getenv("MODEL_EMBEDDING", "intfloat/multilingual-e5-large"))
#     embedding_model = SentenceTransformer(os.getenv("MODEL_EMBEDDING", "intfloat/multilingual-e5-large"))
#     models_cache["embedding_model"] = embedding_model
#     models_cache["qdrant_client"] = QdrantClient(
#         url=os.getenv("QDRANT_URL"),
#         api_key=os.getenv("QDRANT_API_KEY"),
#     )
#     models_cache["llm_rag"] = genai.GenerativeModel("gemini-2.5-pro")
#     models_cache["llm_fast"] = genai.GenerativeModel("gemini-2.5-flash")
#     models_cache["vector_dimension"] = embedding_model.get_sentence_embedding_dimension()
    
#     # Startup
#     print("Ứng dụng đang khởi động...")
#     await create_indexes()  # tạo index bất đồng bộ

#     await create_admin_user()
#     print("Các chỉ mục và admin đã được tạo thành công.")
    
#     yield
#     print("Đang đóng kết nối MongoDB...")
#     client.close()
#     print("Kết nối đã được đóng.")
#     # Dọn dẹp khi tắt server
#     models_cache.clear()
#     conversation_histories.close()

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer, CrossEncoder
from google.generativeai.types import GenerationConfig
import google.generativeai as genai
from diskcache import Cache
from dotenv import load_dotenv
from app.models.user import create_admin_user
from app.core.database import create_indexes, client
from app.classification.classify import load_all_models

load_dotenv()

models_cache = {}
conversation_histories = Cache("cache/chat_histories")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("⏳ Đang khởi tạo models...")
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    # 1. Embedding Model (e5-large)
    embedding_model = SentenceTransformer(os.getenv("MODEL_EMBEDDING", "intfloat/multilingual-e5-large"))
    models_cache["embedding_model"] = embedding_model
    
    # 2. Re-ranker Model (QUAN TRỌNG: Model này giúp tăng điểm Precision)
    print("⏳ Đang tải Re-ranker (BAAI/bge-reranker-v2-m3)...")
    reranker_model = CrossEncoder('BAAI/bge-reranker-v2-m3', max_length=512)
    models_cache["reranker_model"] = reranker_model

    # 3. Qdrant & Gemini
    models_cache["qdrant_client"] = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
    )
    
    rag_config = GenerationConfig(
        temperature=0.2, # Thấp để bám sát context (0.0 - 1.0)
        top_p=0.95,      # Lấy xác suất tích lũy top 95%
    )

    # Cấu hình cho Model nhanh (Phân loại/JSON cần chính xác tuyệt đối)
    fast_config = GenerationConfig(
        temperature=0.1, # Rất thấp để format JSON chuẩn
        top_p=0.95,
        max_output_tokens=1024,
    )
    # models_cache["llm_rag"] = genai.GenerativeModel("gemini-2.5-pro")
    models_cache["llm_rag"] = genai.GenerativeModel("gemini-2.5-flash")
    models_cache["llm_fast"] = genai.GenerativeModel("gemini-2.5-flash-lite")
    # models_cache["llm_fast"] = genai.GenerativeModel("gemini-2.5-flash")
    # models_cache["llm_rag"] = genai.GenerativeModel("gemini-2.5-flash-lite")
    # models_cache["llm_rag"] = genai.GenerativeModel("gemma-3-27b-it")
    # models_cache["llm_fast"] = genai.GenerativeModel("gemma-3-27b-it")
    models_cache["vector_dimension"] = embedding_model.get_sentence_embedding_dimension()
    
    await create_indexes()
    await create_admin_user()

    # Load CNN models vào bộ nhớ (chỉ 1 lần khi server khởi động)
    print("⏳ Đang load CNN models (ConvNeXtV2 + ResNet101)...")
    try:
        load_all_models()
        print("✅ CNN models đã load thành công!")
    except Exception as e:
        print(f"⚠️ CNN models load thất bại (sẽ bỏ qua phân loại ảnh): {e}")
    
    yield
    
    client.close()
    models_cache.clear()
    conversation_histories.close()