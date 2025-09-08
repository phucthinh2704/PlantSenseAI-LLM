from fastapi import APIRouter, HTTPException
from datetime import datetime
import json
from pathlib import Path
from app.core.database import db
from app.schema.response_schema import APIResponse

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent  # trỏ đến gốc project (app/..)
DATA_PLANT_FILE = BASE_DIR / "data" / "plant_data.json"
@router.post("/plants", response_model=APIResponse)
async def seed_plants():
    if not DATA_PLANT_FILE.exists():
        raise HTTPException(status_code=404, detail="plant_data.json not found")

    # Đọc dữ liệu từ file
    with open(DATA_PLANT_FILE, "r", encoding="utf-8") as f:
        plants_data = json.load(f)

    # Thêm timestamp cho mỗi plant
    for plant in plants_data:
        plant["created_at"] = datetime.utcnow()
        plant["updated_at"] = datetime.utcnow()

    # Xóa dữ liệu cũ trước khi seed
    await db.plants.delete_many({})

    # Insert dữ liệu mới
    result = await db.plants.insert_many(plants_data)

    return APIResponse(
        success=True,
        message=f"Seeded {len(result.inserted_ids)} plants successfully",
        data={"inserted_ids": [str(_id) for _id in result.inserted_ids]},
    )
