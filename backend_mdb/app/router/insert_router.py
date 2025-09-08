from fastapi import APIRouter, HTTPException
from datetime import datetime
import json
from pathlib import Path
from app.core.database import db
from app.schema.response_schema import APIResponse

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent  # trỏ đến gốc project (app/..)
DATA_PLANT_FILE = BASE_DIR / "data" / "plant_data.json"
DATA_DISEASE_FILE = BASE_DIR / "data" / "disease_data.json"
DATA_CULTIVATION_FILE = BASE_DIR / "data" / "cultivation_data.json"
DATA_STAGE_FILE = BASE_DIR / "data" / "disease_stage_data.json"


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


@router.post("/diseases", response_model=APIResponse)
async def seed_diseases():
    if not DATA_DISEASE_FILE.exists():
        raise HTTPException(status_code=404, detail="disease_data.json not found")

    with open(DATA_DISEASE_FILE, "r", encoding="utf-8") as f:
        diseases_data = json.load(f)

    # Thêm timestamp cho mỗi disease
    for disease in diseases_data:
        disease["created_at"] = datetime.utcnow()
        disease["updated_at"] = datetime.utcnow()

    # Xóa dữ liệu cũ trước khi seed
    await db.diseases.delete_many({})

    # Insert dữ liệu mới
    result = await db.diseases.insert_many(diseases_data)

    return APIResponse(
        success=True,
        message=f"Seeded {len(result.inserted_ids)} diseases successfully",
        data={"inserted_ids": [str(_id) for _id in result.inserted_ids]},
    )


@router.post("/cultivations", response_model=APIResponse)
async def seed_cultivations():
    if not DATA_CULTIVATION_FILE.exists():
        raise HTTPException(status_code=404, detail="cultivation_data.json not found")

    with open(DATA_CULTIVATION_FILE, "r", encoding="utf-8") as f:
        cultivations_data = json.load(f)

    for item in cultivations_data:
        item["created_at"] = datetime.utcnow()
        item["updated_at"] = datetime.utcnow()

    await db.cultivation_techniques.delete_many({})
    result = await db.cultivation_techniques.insert_many(cultivations_data)

    return APIResponse(
        success=True,
        message=f"Seeded {len(result.inserted_ids)} cultivation techniques successfully",
        data={"inserted_ids": [str(_id) for _id in result.inserted_ids]},
    )


@router.post("/disease_stages", response_model=APIResponse)
async def seed_disease_stages():
    if not DATA_STAGE_FILE.exists():
        raise HTTPException(status_code=404, detail="disease_stage_data.json not found")

    with open(DATA_STAGE_FILE, "r", encoding="utf-8") as f:
        stages_data = json.load(f)

    for item in stages_data:
        item["created_at"] = datetime.utcnow()
        item["updated_at"] = datetime.utcnow()

    await db.disease_stages.delete_many({})
    result = await db.disease_stages.insert_many(stages_data)

    return APIResponse(
        success=True,
        message=f"Seeded {len(result.inserted_ids)} disease stages successfully",
        data={"inserted_ids": [str(_id) for _id in result.inserted_ids]},
    )
