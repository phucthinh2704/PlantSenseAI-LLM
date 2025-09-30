import os
import uuid
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Filter, FieldCondition, MatchValue
from dotenv import load_dotenv
import re

load_dotenv()

# ==== Qdrant config ====
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "intfloat/multilingual-e5-large")

qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)

def init_qdrant(recreate: bool = False):
    try:
        exists = qdrant.collection_exists(collection_name=COLLECTION_NAME)
    except Exception:
        collections = qdrant.get_collections().collections
        exists = COLLECTION_NAME in [c.name for c in collections]

    if recreate and exists:
        qdrant.delete_collection(collection_name=COLLECTION_NAME)
        exists = False

    if not exists:
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1024, distance="Cosine"),
        )
        print(f"🗂️ Created Qdrant collection `{COLLECTION_NAME}`")

        # 🚀 Thêm index cho các trường cần filter
        qdrant.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="type",
            field_schema="keyword"
        )
        qdrant.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="plant_id",
            field_schema="keyword"
        )
        qdrant.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="disease_id",
            field_schema="keyword"
        )
    else:
        print(f"🗂️ Qdrant collection `{COLLECTION_NAME}` already exists")

# ✨ Chunk theo câu/đoạn thay vì số từ
def chunk_text(text: str, max_length: int = 300):
    sentences = re.split(r'(?<=[.!?]) +', text)  # cắt theo câu
    chunks, current = [], ""
    for sentence in sentences:
        if len((current + " " + sentence).split()) <= max_length:
            current += " " + sentence
        else:
            chunks.append(current.strip())
            current = sentence
    if current:
        chunks.append(current.strip())
    return chunks

def upsert_text(text: str, metadata: dict):
    if not text or text.strip() == "":
        return
    chunks = chunk_text(text)
    points = []
    for chunk in chunks:
        vector = embedder.encode(chunk).tolist()
        points.append(
            {
                "id": str(uuid.uuid4()),
                "vector": vector,
                "payload": {"text": chunk, **metadata},
            }
        )
    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)

def upsert_full_text(text: str, metadata: dict):
    if not text or text.strip() == "":
        return
    vector = embedder.encode(text).tolist()
    point = {
        "id": str(uuid.uuid4()),
        "vector": vector,
        "payload": {"text": text, **metadata},
    }
    qdrant.upsert(collection_name=COLLECTION_NAME, points=[point])

# ✨ Search có hỗ trợ filter theo type / plant_id / disease_id
# def search_documents(query_text: str, top_k: int = 5, filters: dict = None):
#     if not query_text or query_text.strip() == "":
#         return []

#     query_vector = embedder.encode(query_text).tolist()

#     qdrant_filter = None
#     if filters:
#         conditions = []
#         for k, v in filters.items():
#             conditions.append(FieldCondition(key=k, match=MatchValue(value=v)))
#         qdrant_filter = Filter(must=conditions)

#     results = qdrant.search(
#         collection_name=COLLECTION_NAME,
#         query_vector=query_vector,
#         limit=top_k,
#         query_filter=qdrant_filter,
#     )

#     docs = []
#     for r in results:
#         docs.append(
#             {
#                 "id": r.id,
#                 "score": r.score,
#                 "text": r.payload.get("text"),
#                 "metadata": {k: v for k, v in r.payload.items() if k != "text"},
#             }
#         )
#     return docs
def search_documents(query_text: str, top_k: int = 5, filters: dict = None):
    if not query_text or query_text.strip() == "":
        return []

    query_vector = embedder.encode(query_text).tolist()

    qdrant_filter = None
    if filters:
        must_conditions = []
        for key, value in filters.items():
            must_conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
        qdrant_filter = Filter(must=must_conditions)

    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
        query_filter=qdrant_filter,  # ✅ thêm filter
    )

    docs = []
    for r in results:
        docs.append(
            {
                "id": r.id,
                "score": r.score,
                "text": r.payload.get("text"),
                "metadata": {k: v for k, v in r.payload.items() if k != "text"},
            }
        )
    return docs