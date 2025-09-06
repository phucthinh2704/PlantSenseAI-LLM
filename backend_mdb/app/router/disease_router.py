from fastapi import APIRouter, HTTPException, Query
from app.models.diseases import Disease
from app.schema.response_schema import APIResponse
from app.services import disease_service

router = APIRouter(prefix="/diseases", tags=["Diseases"])


@router.post("/", response_model=APIResponse)
async def create_disease(disease: Disease):
    inserted_id = await disease_service.create_disease(disease.model_dump())
    return APIResponse(
        success=True, message="Disease created", data={"inserted_id": inserted_id}
    )


@router.get("/", response_model=APIResponse)
async def get_diseases(
    plant_id: str | None = Query(None), stage: str | None = Query(None)
):
    """
    Nếu truyền plant_id => lọc theo cây trồng
    Nếu truyền thêm stage => lọc theo giai đoạn cây
    Nếu không truyền gì => lấy tất cả
    """
    if plant_id and stage:
        diseases = await disease_service.get_diseases_by_plant_and_stage(
            plant_id, stage
        )
    elif plant_id:
        diseases = await disease_service.get_diseases_by_plant(plant_id)
    else:
        diseases = await disease_service.get_all_diseases()
    return APIResponse(success=True, message="Diseases retrieved", data=diseases)


@router.get("/{disease_id}", response_model=APIResponse)
async def get_disease(disease_id: str):
    disease = await disease_service.get_disease_by_id(disease_id)
    if not disease:
        raise HTTPException(status_code=404, detail="Disease not found")
    return APIResponse(success=True, message="Disease retrieved", data=disease)


@router.put("/{disease_id}", response_model=APIResponse)
async def update_disease(disease_id: str, disease: Disease):
    updated = await disease_service.update_disease(
        disease_id, disease.model_dump(exclude_unset=True)
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Disease not found or not updated")
    return APIResponse(success=True, message="Disease updated")


@router.delete("/{disease_id}", response_model=APIResponse)
async def delete_disease(disease_id: str):
    deleted = await disease_service.delete_disease(disease_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Disease not found")
    return APIResponse(success=True, message="Disease deleted")
