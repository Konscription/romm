from fastapi import APIRouter, HTTPException

from backend.config.cheat_type_manager import cheat_type_manager

router = APIRouter(
    tags=["cheat_types"],
    responses={404: {"description": "Not found"}},
)


@router.get("/cheat_types", response_model=list)
def get_cheat_types():
    """Get all cheat types"""
    return list(cheat_type_manager.get_cheat_types().values())


@router.get("/cheat_types/{type_id}", response_model=dict)
def get_cheat_type(type_id: str):
    """Get a specific cheat type by ID"""
    cheat_type = cheat_type_manager.get_cheat_type(type_id)
    if cheat_type is None:
        raise HTTPException(status_code=404, detail="Cheat type not found")
    return cheat_type


@router.post("/cheat_types", response_model=dict)
def create_cheat_type(type_id: str, type_data: dict):
    """Create a new cheat type"""
    if type_id in cheat_type_manager.get_all_type_ids():
        raise HTTPException(status_code=400, detail="Cheat type already exists")

    cheat_type_manager.add_cheat_type(type_id, type_data)
    return cheat_type_manager.get_cheat_type(type_id)


@router.put("/cheat_types/{type_id}", response_model=dict)
def update_cheat_type(type_id: str, type_data: dict):
    """Update an existing cheat type"""
    if type_id not in cheat_type_manager.get_all_type_ids():
        raise HTTPException(status_code=404, detail="Cheat type not found")

    cheat_type_manager.update_cheat_type(type_id, type_data)
    return cheat_type_manager.get_cheat_type(type_id)


@router.delete("/cheat_types/{type_id}", response_model=dict)
def delete_cheat_type(type_id: str):
    """Delete a cheat type"""
    if type_id not in cheat_type_manager.get_all_type_ids():
        raise HTTPException(status_code=404, detail="Cheat type not found")

    cheat_type = cheat_type_manager.get_cheat_type(type_id)
    cheat_type_manager.delete_cheat_type(type_id)
    return cheat_type
