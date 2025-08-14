from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from ai import service

router = APIRouter()

@router.post("/recipes/upload")
async def upload_recipe_image(
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return await service.analyze_image_and_search_recipes(image, db)
