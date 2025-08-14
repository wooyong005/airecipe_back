import os
import shutil
from fastapi import HTTPException, UploadFile
from collections import Counter
from ai.ai_model import model
from sqlalchemy.orm import Session
from recipe.service import get_recipe  # recipe 검색 함수 재활용

UPLOAD_DIR = "temp_uploads"


async def save_image_file(image: UploadFile) -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, image.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    except Exception as e:
        raise HTTPException(500, f"파일 저장 실패: {str(e)}")
    return file_path


def run_yolo_inference(file_path: str) -> list:
    try:
        results = model(file_path)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(500, f"YOLO 추론 실패: {str(e)}")

    food_names = []
    names = model.names
    for r in results:
        if hasattr(r, "boxes"):
            for box in r.boxes:
                class_id = int(box.cls[0])
                label = names[class_id]
                food_names.append(label)

    os.remove(file_path)

    if not food_names:
        raise HTTPException(404, "이미지에서 음식을 인식하지 못했습니다.")

    return food_names


def get_representative_food_name(food_names: list) -> str:
    common_food_name = Counter(food_names).most_common(1)[0][0]
    if "_" in common_food_name:
        _, search_name = common_food_name.split("_", 1)
    else:
        search_name = common_food_name
    return search_name


async def analyze_image_and_search_recipes(image: UploadFile, db: Session):
    file_path = await save_image_file(image)
    food_names = run_yolo_inference(file_path)
    search_name = get_representative_food_name(food_names)
    recipes = get_recipe(search_name, db)
    if not recipes:
        raise HTTPException(404, f"{search_name} 기반 검색 결과가 없습니다.")
    return recipes
