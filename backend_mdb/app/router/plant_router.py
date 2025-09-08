from fastapi import APIRouter, HTTPException
from app.models.plant import Plant
from app.schema.response_schema import APIResponse
from app.services import plant_service, disease_service, disease_stage_service, cultivation_service
from app.core.database import db

router = APIRouter()


@router.post("/", response_model=APIResponse)
async def create_plant(plant: Plant):
    inserted_id = await plant_service.create_plant(plant.model_dump(by_alias=True))
    return APIResponse(
        success=True, message="Plant created", data={"inserted_id": inserted_id}
    )


@router.get("/", response_model=APIResponse)
async def get_plants():
    plants = await plant_service.get_all_plants()
    return APIResponse(success=True, message="Plants retrieved", data=plants)


@router.get("/{plant_id}", response_model=APIResponse)
async def get_plant(plant_id: str):
    plant = await plant_service.get_plant_by_id(plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return APIResponse(success=True, message="Plant retrieved", data=plant)


@router.get("/{plant_id}/details", response_model=APIResponse)
async def get_plant_details(plant_id: str):
    result = await plant_service.get_plant_details(plant_id)
    if not result:
        raise HTTPException(status_code=404, detail="Plant not found")
    return APIResponse(success=True, message="Plant details retrieved", data=result)


@router.put("/{plant_id}", response_model=APIResponse)
async def update_plant(plant_id: str, plant: Plant):
    updated = await plant_service.update_plant(
        plant_id, plant.model_dump(exclude_unset=True)
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Plant not found or not updated")
    return APIResponse(success=True, message="Plant updated")


@router.delete("/{plant_id}", response_model=APIResponse)
async def delete_plant(plant_id: str):
    deleted = await plant_service.delete_plant(plant_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Plant not found")
    return APIResponse(success=True, message="Plant deleted")


@router.post("/seed", response_model=APIResponse)
async def seed_database():
    await db.plants.delete_many({})
    await db.diseases.delete_many({})
    await db.disease_stages.delete_many({})
    await db.cultivation_techniques.delete_many({})

    # --- 2. Seed Plant ---
    plant_data = {
        "name": "Lúa OM5451",
        "origin": "Việt Nam",
        "category": "Lúa",
        "growth_duration": "105 ngày",
        "morphology": "Thân cứng, cao 90-95cm, lá xanh đậm, hạt dài trắng",
        "yields": "6-7 tấn/ha",
        "description": "Giống lúa OM5451 thích hợp vùng ĐBSCL, năng suất cao.",
        "image_url": "https://example.com/om5451.png",
    }
    plant_id = await plant_service.create_plant(plant_data)

    # --- 3. Seed Disease ---
    disease_data = {
        "name": "Bệnh đạo ôn lá",
        "cause": "Nấm Pyricularia oryzae",
        "image_url": "https://example.com/dao_on.png",
        "plant_ids": [plant_id],
    }
    disease_id = await disease_service.create_disease(disease_data)

    # --- 4. Seed Disease Stages ---
    stage_docs = [
        {
            "disease_id": disease_id,
            "stage": "Mạ",
            "symptom": "Vết bệnh hình thoi, màu xám trắng, làm lá cháy khô.",
            "prevention": [
                {
                    "step": 1,
                    "name": "Vệ sinh đồng ruộng",
                    "description": "Dọn sạch cỏ, tàn dư rơm rạ trước khi gieo sạ",
                },
                {
                    "step": 2,
                    "name": "Chọn giống kháng bệnh",
                    "description": "Sử dụng giống có khả năng chống chịu",
                },
            ],
            "treatment": [
                {
                    "step": 1,
                    "name": "Phun thuốc lần 1",
                    "description": "Phun thuốc khi bệnh chớm xuất hiện giai đoạn 20-25 ngày sau sạ",
                    "chemical": "Tricyclazole 75WP",
                    "dosage": "150g/ha",
                }
            ],
        },
        {
            "disease_id": disease_id,
            "stage": "Đẻ nhánh",
            "symptom": "Bệnh lan rộng làm lá cháy thành mảng",
            "prevention": [],
            "treatment": [
                {
                    "step": 1,
                    "name": "Phun thuốc lần 2",
                    "description": "Lặp lại sau 5-7 ngày nếu bệnh vẫn còn",
                    "chemical": "Isoprothiolane",
                    "dosage": "200g/ha",
                }
            ],
        },
    ]

    for stage in stage_docs:
        await disease_stage_service.create_stage(stage)

    # --- 5. Seed Cultivation Technique ---
    cultivation_data = {
        "plant_id": plant_id,
        "season": "Vụ Đông Xuân",
        "steps": [
            {"step": 1, "name": "Làm đất", "description": "Cày xới đất, xử lý rơm rạ trước khi sạ 2 tuần."},
            {"step": 2, "name": "Gieo sạ", "description": "Sạ thưa, mật độ 100-120kg/ha."},
            {"step": 3, "name": "Bón phân", "description": "Chia 3 lần bón: lót, thúc đẻ nhánh, đòng."},
            {"step": 4, "name": "Phòng trừ sâu bệnh", "description": "Theo dõi thường xuyên, phun thuốc khi cần thiết."},
        ],
    }
    cultivation_id = await cultivation_service.create_cultivation(cultivation_data)

    return APIResponse(
        success=True,
        message="Database seeded successfully",
        data={
            "plant_id": plant_id,
            "disease_id": disease_id,
            "cultivation_id": cultivation_id,
        },
    )

