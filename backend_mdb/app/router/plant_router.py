# app/routes/plant_router.py
from fastapi import APIRouter, HTTPException
from app.models.plant import Plant
from app.services import plant_service
from app.schema.response_schema import APIResponse
from datetime import datetime
from app.core.database import db

router = APIRouter()


@router.post("/", response_model=APIResponse)
async def create_plant(plant: Plant):
    inserted_id = await plant_service.create_plant(plant.model_dump(by_alias=True))
    return APIResponse(
        success=True,
        message="Plant created successfully",
        data={"inserted_id": inserted_id},
    )


@router.get("/", response_model=APIResponse)
async def get_plants():
    plants = await plant_service.get_all_plants()
    return APIResponse(
        success=True, message="Plants retrieved successfully", data=plants
    )


@router.get("/{plant_id}", response_model=APIResponse)
async def get_plant(plant_id: str):
    plant = await plant_service.get_plant_by_id(plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return APIResponse(success=True, message="Plant retrieved successfully", data=plant)


@router.get("/{plant_id}/details", response_model=APIResponse)
async def get_plant_details(plant_id: str):
    result = await plant_service.get_plant_details(plant_id)
    if not result:
        raise HTTPException(status_code=404, detail="Plant not found")
    return APIResponse(
        success=True,
        message="Plant details retrieved successfully",
        data=result,
    )


@router.put("/{plant_id}", response_model=APIResponse)
async def update_plant(plant_id: str, plant: Plant):
    updated = await plant_service.update_plant(
        plant_id, plant.model_dump(exclude_unset=True)
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Plant not found or not updated")
    return APIResponse(success=True, message="Plant updated successfully")


@router.delete("/{plant_id}", response_model=APIResponse)
async def delete_plant(plant_id: str):
    deleted = await plant_service.delete_plant(plant_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Plant not found")
    return APIResponse(success=True, message="Plant deleted successfully")


@router.get("/by_category/{category}", response_model=APIResponse)
async def get_by_category(category: str):
    plants = await plant_service.get_plants_by_category(category)
    return APIResponse(
        success=True, message="Plants retrieved successfully", data=plants
    )


@router.get("/by_name/{name}", response_model=APIResponse)
async def get_by_name(name: str):
    plants = await plant_service.get_plants_by_name(name)
    return APIResponse(
        success=True, message="Plants retrieved successfully", data=plants
    )


@router.get("/by_disease/{disease_name}", response_model=APIResponse)
async def get_by_disease(disease_name: str):
    plants = await plant_service.get_plants_by_disease(disease_name)
    return APIResponse(
        success=True, message="Plants retrieved successfully", data=plants
    )


@router.post("/seed", response_model=APIResponse)
async def seed_database():
    # Xóa dữ liệu cũ
    await db.plants.delete_many({})
    await db.diseases.delete_many({})
    await db.cultivation_techniques.delete_many({})

    # Seed Plant
    plant_data = {
        "name": "Lúa OM5451",
        "scientific_name": "Oryza sativa",
        "origin": "Việt Nam",
        "category": "Lúa",
        "growth_duration_days": 105,
        "morphology": {
            "height": "90-95cm",
            "stem": "Thân cứng, chống đổ tốt",
            "leaf": "Lá xanh đậm, dạng đứng",
            "grain": "Hạt dài, trắng, cơm mềm",
        },
        "description": "Giống lúa OM5451 thích hợp vùng ĐBSCL, năng suất cao.",
        "image_url": "https://example.com/om5451.png",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    plant_result = await db.plants.insert_one(plant_data)
    plant_id = str(plant_result.inserted_id)

    # Seed Disease
    disease_data = {
        "name": "Bệnh đạo ôn lá",
        "cause": "Nấm Pyricularia oryzae",
        "symptom": "Vết bệnh hình thoi, màu xám trắng, làm lá cháy khô.",
        "prevention": [
            {
                "step": 1,
                "name": "Vệ sinh đồng ruộng",
                "description": "Dọn sạch cỏ, tàn dư rơm rạ.",
            },
            {
                "step": 2,
                "name": "Chọn giống kháng bệnh",
                "description": "Sử dụng giống có khả năng chống chịu.",
            },
        ],
        "treatment": [
            {
                "step": 1,
                "name": "Phun thuốc",
                "description": "Sử dụng thuốc trừ đạo ôn giai đoạn 20-25 ngày sau sạ",
                "chemical": "Tricyclazole",
                "dosage": "150g/ha",
            }
        ],
        "image_url": "https://example.com/dao_on.png",
        "plant_ids": [plant_id],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    await db.diseases.insert_one(disease_data)

    # 3️Seed Cultivation Technique
    cultivation_data = {
        "plant_id": plant_id,
        "season": "Vụ Đông Xuân",
        "steps": [
            {
                "step": 1,
                "name": "Làm đất",
                "description": "Cày xới đất, xử lý rơm rạ trước khi sạ 2 tuần.",
            },
            {
                "step": 2,
                "name": "Gieo sạ",
                "description": "Sạ thưa, mật độ 100-120kg/ha.",
            },
            {
                "step": 3,
                "name": "Bón phân",
                "description": "Chia 3 lần bón: lót, thúc đẻ nhánh, đòng.",
            },
            {
                "step": 4,
                "name": "Phòng trừ sâu bệnh",
                "description": "Theo dõi thường xuyên, phun thuốc khi cần thiết.",
            },
        ],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    await db.cultivation_techniques.insert_one(cultivation_data)

    return APIResponse(success=True, message="Database seeded successfully")
