from fastapi import APIRouter, HTTPException
from app.models.cultivation_techniques import CultivationTechnique
from app.services import cultivation_service
from app.schema.response_schema import APIResponse

router = APIRouter()


@router.post("/", response_model=APIResponse)
async def create_cultivation(cultivation: CultivationTechnique):
    inserted_id = await cultivation_service.create_cultivation(
        cultivation.model_dump(by_alias=True)
    )
    return APIResponse(
        success=True, message="Cultivation created", data={"inserted_id": inserted_id}
    )


@router.get("/", response_model=APIResponse)
async def get_cultivations():
    cultivations = await cultivation_service.get_all_cultivations()
    return APIResponse(
        success=True, message="Cultivations retrieved", data=cultivations
    )


@router.get("/by_plant/{plant_id}", response_model=APIResponse)
async def get_by_plant(plant_id: str):
    cultivations = await cultivation_service.get_cultivations_by_plant(plant_id)
    return APIResponse(
        success=True, message="Cultivations retrieved", data=cultivations
    )


@router.get("/{cultivation_id}", response_model=APIResponse)
async def get_cultivation(cultivation_id: str):
    cultivation = await cultivation_service.get_cultivation_by_id(cultivation_id)
    if not cultivation:
        raise HTTPException(status_code=404, detail="Cultivation not found")
    return APIResponse(success=True, message="Cultivation retrieved", data=cultivation)


@router.put("/{cultivation_id}", response_model=APIResponse)
async def update_cultivation(cultivation_id: str, cultivation: CultivationTechnique):
    updated = await cultivation_service.update_cultivation(
        cultivation_id, cultivation.model_dump(exclude_unset=True)
    )
    if not updated:
        raise HTTPException(
            status_code=404, detail="Cultivation not found or not updated"
        )
    return APIResponse(success=True, message="Cultivation updated")


@router.delete("/{cultivation_id}", response_model=APIResponse)
async def delete_cultivation(cultivation_id: str):
    deleted = await cultivation_service.delete_cultivation(cultivation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Cultivation not found")
    return APIResponse(success=True, message="Cultivation deleted")
