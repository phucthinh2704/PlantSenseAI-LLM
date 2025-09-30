from fastapi import APIRouter, Query
from typing import Optional
from app.services.qdrant_service import search_documents, init_qdrant
from app.services.ingest_service import ingest

router = APIRouter()

@router.get("/search")
def search(
    query: str = Query(..., description="Câu hỏi tìm kiếm"),
    top_k: int = 5,
    type: Optional[str] = Query(None, description="Loại dữ liệu (plant, disease, cultivation, disease_stage)"),
    plant_id: Optional[str] = Query(None, description="ID của cây trồng"),
    disease_id: Optional[str] = Query(None, description="ID của bệnh")
):
    # 🔹 Xây dựng filters động
    filters = {}
    if type:
        filters["type"] = type
    if plant_id:
        filters["plant_id"] = plant_id
    if disease_id:
        filters["disease_id"] = disease_id

    results = search_documents(query, top_k, filters=filters if filters else None)
    return {"query": query, "results": results}


@router.post("/init")
async def init_data():
    init_qdrant(recreate=True)
    return {"message": "Qdrant initialized!"}


@router.post("/ingest")
async def ingest_data():
    await ingest()
    return {"message": "Ingestion completed!"}
