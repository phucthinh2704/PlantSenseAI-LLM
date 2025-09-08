from fastapi import APIRouter, HTTPException, Query
from app.models.disease_stage import DiseaseStage
from app.services import disease_stage_service
from app.schema.response_schema import APIResponse

router = APIRouter()


@router.post("/", response_model=APIResponse)
async def create_stage(stage: DiseaseStage):
    inserted_id = await disease_stage_service.create_stage(stage.model_dump(by_alias=True))
    return APIResponse(success=True, message="Disease stage created", data={"inserted_id": inserted_id})


@router.get("/", response_model=APIResponse)
async def get_stages(disease_id: str | None = Query(None)):
    stages = (
        await disease_stage_service.get_stages_by_disease(disease_id)
        if disease_id else await disease_stage_service.get_all_stages()
    )
    return APIResponse(success=True, message="Disease stages retrieved", data=stages)


@router.get("/{stage_id}", response_model=APIResponse)
async def get_stage(stage_id: str):
    stage = await disease_stage_service.get_stage_by_id(stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Disease stage not found")
    return APIResponse(success=True, message="Disease stage retrieved", data=stage)


@router.put("/{stage_id}", response_model=APIResponse)
async def update_stage(stage_id: str, stage: DiseaseStage):
    updated = await disease_stage_service.update_stage(stage_id, stage.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Disease stage not found or not updated")
    return APIResponse(success=True, message="Disease stage updated")


@router.delete("/{stage_id}", response_model=APIResponse)
async def delete_stage(stage_id: str):
    deleted = await disease_stage_service.delete_stage(stage_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Disease stage not found")
    return APIResponse(success=True, message="Disease stage deleted")
