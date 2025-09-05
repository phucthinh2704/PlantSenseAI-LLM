from fastapi import APIRouter, HTTPException
from app.models.diseases import Disease
from app.services import disease_service
from app.schema.response_schema import APIResponse

router = APIRouter()

@router.post("/")
async def create_disease(disease: Disease):
    inserted_id = await disease_service.create_disease(disease.model_dump())
    return APIResponse(success=True, message="Disease created", data={"inserted_id": inserted_id})

@router.get("/")
async def get_diseases():
    diseases = await disease_service.get_all_diseases()
    return APIResponse(success=True, message="Diseases retrieved", data=diseases)

@router.get("/{disease_id}")
async def get_disease(disease_id: str):
    disease = await disease_service.get_disease_by_id(disease_id)
    if not disease:
        raise HTTPException(status_code=404, detail="Disease not found")
    return APIResponse(success=True, message="Disease retrieved", data=disease)

@router.get("/by_plant/{plant_id}")
async def get_by_plant(plant_id: str):
    diseases = await disease_service.get_diseases_by_plant(plant_id)
    return APIResponse(success=True, message="Diseases retrieved", data=diseases)

@router.put("/{disease_id}")
async def update_disease(disease_id: str, disease: Disease):
    updated = await disease_service.update_disease(disease_id, disease.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Disease not found or not updated")
    return APIResponse(success=True, message="Disease updated")

@router.delete("/{disease_id}")
async def delete_disease(disease_id: str):
    deleted = await disease_service.delete_disease(disease_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Disease not found")
    return APIResponse(success=True, message="Disease deleted")
