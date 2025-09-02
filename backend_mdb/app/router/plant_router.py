from fastapi import APIRouter, HTTPException
from app.models.plant import Plant
from app.services import plant_service
from app.schema.response_schema import APIResponse

router = APIRouter()


@router.post("/")
def create_plant(plant: Plant):
    inserted_id = plant_service.create_plant(plant.model_dump())
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


@router.get("/by_category/{category}")
async def get_by_category(category: str):
    plants = await plant_service.get_plants_by_category(category)
    if not plants:
        raise HTTPException(status_code=404, detail=f"No plant found in category: {category}")
    return APIResponse(success=True, message="Plants retrieved successfully", data=plants)


@router.get("/by_name/{name}")
async def get_by_name(name: str):
    plants = await plant_service.get_plants_by_name(name)
    if not plants:
        raise HTTPException(status_code=404, detail=f"No plant found with name: {name}")
    return APIResponse(success=True, message="Plants retrieved successfully", data=plants)


@router.get("/by_disease/{disease_name}")
async def get_by_disease(disease_name: str):
    plants = await plant_service.get_plants_by_disease(disease_name)
    if not plants:
        raise HTTPException(
            status_code=404, detail=f"No plant found with disease: {disease_name}"
        )
    return APIResponse(
        success=True, message="Plants retrieved successfully", data=plants
    )
