import asyncio
from bson import ObjectId
from app.core.database import db
from app.services.qdrant_service import upsert_full_text, upsert_text


async def ingest():
    # (a) Plants
    async for plant in db.plants.find({}):
        text = (
            f"Giống {plant['name']} có nguồn gốc {plant.get('origin','')}."
            f" Thời gian sinh trưởng: {plant.get('growth_duration','')}."
            f" Hình thái: {plant.get('morphology','')}."
            f" Năng suất: {plant.get('yields','')}."
            f" Mô tả: {plant.get('description','')}"
        )
        upsert_full_text(
            text,
            {
                "type": "plant",
                "plant_id": str(plant["_id"]),
                "name": plant["name"],
                "origin": plant.get("origin"),
                "image_url": plant.get("image_url"),
            },
        )

    # (b) Diseases (populate plant_names)
    async for disease in db.diseases.find({}):
        plant_ids = disease.get("plant_ids", [])
        plants = []
        plant_names = []

        if plant_ids:
            plants = await db.plants.find(
                {"_id": {"$in": [ObjectId(pid) for pid in plant_ids]}}
            ).to_list(None)
            plant_names = [p["name"] for p in plants]

        text = (
            f"Bệnh {disease['name']} ảnh hưởng đến cây {', '.join(plant_names) if plant_names else 'không rõ'}."
            f" Nguyên nhân: {disease.get('cause','')}."
        )

        upsert_full_text(
            text,
            {
                "type": "disease",
                "disease_id": str(disease["_id"]),
                "name": disease["name"],
                "plant_ids": plant_ids,
                "plant_names": plant_names,  # ✅ thêm plant_names vào payload
                "image_url": disease.get("image_url"),
            },
        )

    # (c) Disease stages
    async for stage in db.disease_stages.find({}):
        stage_text = f"Ở giai đoạn {stage['stage']}, triệu chứng: {stage['symptom']}."
        for p in stage.get("prevention", []):
            stage_text += f" Phòng ngừa: {p['description']}."
        for t in stage.get("treatment", []):
            stage_text += f" Điều trị: {t['description']} {t.get('chemical','')} {t.get('dosage','')}."
        upsert_text(
            stage_text,
            {
                "type": "disease_stage",
                "disease_id": stage["disease_id"],
                "stage": stage["stage"],
            },
        )

    # (d) Cultivation techniques
    async for ct in db.cultivation_techniques.find({}):
        text = f"Kỹ thuật canh tác cho cây {ct['plant_id']} trong mùa {ct.get('season','')}."
        for step in ct.get("steps", []):
            text += f" Bước {step['step']}: {step['name']} - {step['description']}."
        upsert_text(
            text,
            {
                "type": "cultivation",
                "plant_id": ct["plant_id"],
                "season": ct.get("season"),
            },
        )

    print("✅ Ingestion hoàn tất! Dữ liệu đã được đưa vào Qdrant.")


def run_ingest():
    asyncio.run(ingest())
