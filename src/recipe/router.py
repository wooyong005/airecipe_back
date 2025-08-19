#  recipe/router.py

# 기존 # route/recipe.py 의 내용 대부분.

from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_, distinct, desc
from database import get_db

# recipe 폴더 내 모델
from .models import Rating, Recipe, RecipeRatingHistories, PeriodTypeEnum

# user 폴더 내 모델
from user.models import UserSearchHistory, UserBmiRecommendation, UserDetail, UserFavorites

# service 모듈 전체 임포트 
from . import service  

from recipe.service import translate_texts # 구글트랜스도 임포트 # 정용우추가 # 위에 모듈 전체 임포트로 안되서 따로 함.

# schemas
from .schemas import RatingRequest, FavoriteRequest, SearchHistoryRequest, BmiRecommendationRequest

from datetime import date, timedelta, datetime
import shutil
import os
from collections import Counter
from ai.ai_model import model
from typing import List, Optional

from chatbot.chatbot import ask_chatbot # 정용우 추가
from pydantic import BaseModel # 정용우 추가 # 요청 바디(JSON)**를 자동으로 파이썬 객체로 변환 # 클라이언트가 "레시피 알려줘"> request.message 로 사용
from fastapi.responses import StreamingResponse # 스트리밍 서비스 # 정용우 추가
#from chatbot import model # 정용우 추가 이거 뭔가 안돼서 아래 3줄추가.
import google.generativeai as genai # 정용우

genai.configure(api_key="AIzaSyDnMIpa9qzRUdMvX5FvH4v13JOhWfjzkIs") # 정용우
gemini_model = genai.GenerativeModel("gemini-1.5-flash") # 정용우




router = APIRouter()


# ---------------------------------
# Helper
# ---------------------------------
def classify_bmi(bmi: float) -> str:
    if bmi < 18.5:
        return "저체중"
    elif bmi < 23:
        return "정상"
    elif bmi < 25:
        return "과체중"
    else:
        return "비만"


# ---------------------------------
# 즐겨찾기
# ---------------------------------
@router.post("/favorites")
def favorite_recipe(request: FavoriteRequest, db: Session = Depends(get_db)):
    try:
        fav = service.add_to_favorites(request.user_id, request.recipe_id, db)
        return {"message": "레시피를 즐겨찾기(찜) 추가했습니다."}
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.delete("/favorites")
def unfavorite_recipe(request: FavoriteRequest, db: Session = Depends(get_db)):
    try:
        service.remove_from_favorites(request.user_id, request.recipe_id, db)
        return {"message": "레시피 즐겨찾기(찜) 해제 성공"}
    except ValueError as e:
        raise HTTPException(404, detail=str(e))


@router.get("/favorites/{user_id}")
def get_favorites(user_id: str, db: Session = Depends(get_db)):
    recipes = service.get_user_favorites(user_id, db)
    return {"favorites": [
        {
            "id": r.id,
            "name": r.name,
            "image_url": r.image_url,
            "category": r.category,
            "avg_rating": float(r.avg_rating or 0),
            "rating_count": r.rating_count or 0,
            "view_count": r.view_count or 0,
        }
        for r in recipes if r
    ]}


# ---------------------------------
# 외부 레시피 검색
# ---------------------------------
@router.get("/recipes/external/search")
def search_recipes(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    recipes = service.get_recipe(q, db)
    if not recipes:
        raise HTTPException(404, "레시피가 없습니다.")
    return recipes


# ---------------------------------
# 레시피 상세보기
# ---------------------------------
@router.get("/recipedetail") # 전체적으로 많이 바꿈(순서) # 정용우
async def recipe_detail(
    id: int = Query(...), 
    user_id: Optional[str] = Query(None), # 정용우 수정. optional 추가
    lang: str = Query("ko"), # 언어 설정, 기본값은 한국어 # 정용우 lang추가
    increment_view: bool = Query(True), 
    db: Session = Depends(get_db)
):
    
    
    
    # 1. 레시피 조회 (+조회수 증가 처리)
    if increment_view:
        recipe = service.increase_recipe_view_count(id, db)
    else:
        recipe = db.query(Recipe).filter_by(id=id).first()
    if not recipe:
        raise HTTPException(404, "레시피가 없어요. 챗봇을 이용해주세요.") # 에러 문구 변경

    # 2. 단계 텍스트 및 이미지 추출 
    steps = []        # 텍스트
    step_images = []  # 이미지 URL
    for i in range(1, 21):
        text = getattr(recipe, f"MANUAL{str(i).zfill(2)}")
        img = getattr(recipe, f"MANUAL_IMG{str(i).zfill(2)}")
        if text:
            steps.append(text)
            step_images.append(img)


    # 3. 사용자 평점 조회
    user_rating = 0
    if user_id:
        rating_entry = db.query(Rating).filter_by(recipe_id=id, user_id=user_id).first()
        if rating_entry:
            user_rating = rating_entry.rating


    # 4. 한국어인 경우 → 번역 없이 반환
    if lang.lower() == "ko":
        data = {
            "id": recipe.id,
            "lang": "ko",
            "name": recipe.name,
            "description": recipe.description,
            "image_url": recipe.image_url,
            "category": recipe.category,
            "ingredients": recipe.ingredients.split(",") if recipe.ingredients else [],
            "INFO_ENG": recipe.INFO_ENG,
            "INFO_CAR": recipe.INFO_CAR,
            "INFO_PRO": recipe.INFO_PRO,
            "INFO_FAT": recipe.INFO_FAT,
            "INFO_NA": recipe.INFO_NA,
            "RCP_NA_TIP": recipe.RCP_NA_TIP,
            "avg_rating": float(recipe.avg_rating or 0),
            "rating_count": recipe.rating_count or 0,
            "view_count": recipe.view_count or 0,
            "user_rating": user_rating,
        }

        # 단계 텍스트 및 이미지 포함
        for i in range(len(steps)):
            step_num = str(i + 1).zfill(2)
            data[f"MANUAL{step_num}"] = steps[i]
            data[f"MANUAL_IMG{step_num}"] = step_images[i]

        return data


    # 5. 다국어 번역 처리 (en, ja, zh-cn) #정용우
    try:
        # 기본 텍스트 + 재료 + 요리 단계 모음
        texts_to_translate = [
            recipe.name,
            recipe.description or "",
            recipe.RCP_NA_TIP or ""
        ] + (recipe.ingredients.split(",") if recipe.ingredients else []) + steps

        # 비동기 번역 실행
        translated = await translate_texts(texts_to_translate, dest=lang)

        # 번역 결과 분리
        name = translated[0]
        description = translated[1]
        tip = translated[2]

        ingredients_translated = translated[3:3 + len(recipe.ingredients.split(",")) if recipe.ingredients else 0]
        steps_translated = translated[3 + len(ingredients_translated):]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"번역 실패: {e}")



    # 6. 최종 응답 구성
    return {
        "id": recipe.id,
        "lang": lang,  # 요청된 언어
        "name": name,
        "description": description,
        "image_url": recipe.image_url,
        "category": recipe.category,
        "ingredients": ingredients_translated,
        "steps": steps_translated,
        "step_images": step_images,  # 원본 이미지 그대로 반환
        "INFO_ENG": recipe.INFO_ENG,
        "INFO_CAR": recipe.INFO_CAR,
        "INFO_PRO": recipe.INFO_PRO,
        "INFO_FAT": recipe.INFO_FAT,
        "INFO_NA": recipe.INFO_NA,
        "RCP_NA_TIP": tip,
        "avg_rating": float(recipe.avg_rating or 0),
        "rating_count": recipe.rating_count or 0,
        "view_count": recipe.view_count or 0,
        "user_rating": user_rating,
    }



# ---------------------------------
# 레시피 목록
# ---------------------------------
@router.get("/recipelist")
def recipe_list(db: Session = Depends(get_db)):
    return service.get_recipe_list(db)


# ---------------------------------
# 조회수 증가
# ---------------------------------
@router.post("/recipes/{recipe_id}/view")
def view_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = service.increase_recipe_view_count(recipe_id, db)
    if not recipe:
        raise HTTPException(404, "레시피가 없습니다.")
    return {"view_count": recipe.view_count}


# ---------------------------------
# 별점 등록
# ---------------------------------
@router.post("/recipes/{recipe_id}/rating")
def rate_recipe(recipe_id: int, rating: RatingRequest, db: Session = Depends(get_db)):
    if not (1 <= rating.rating <= 5):
        raise HTTPException(400, "별점은 1~5점 사이여야 합니다.")
    try:
        recipe = service.add_or_update_rating(recipe_id, rating.user_id, rating.rating, db)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    return {"avg_rating": float(recipe.avg_rating), "rating_count": recipe.rating_count}


# ---------------------------------
# 랭킹
# ---------------------------------
@router.get("/rankings")
def get_rankings(period: str = Query(..., regex="^(daily|weekly|monthly)$"), db: Session = Depends(get_db)):
    today = date.today()
    try:
        period_enum = PeriodTypeEnum(period)
    except ValueError:
        raise HTTPException(400, "Invalid period")

    if period_enum == PeriodTypeEnum.daily:
        period_start_date = today
    elif period_enum == PeriodTypeEnum.weekly:
        period_start_date = today - timedelta(days=today.weekday())
    elif period_enum == PeriodTypeEnum.monthly:
        period_start_date = today.replace(day=1)

    avg_rating_expr = RecipeRatingHistories.rating_sum / RecipeRatingHistories.rating_count
    rankings = (
        db.query(Recipe, RecipeRatingHistories)
        .join(RecipeRatingHistories, Recipe.id == RecipeRatingHistories.recipe_id)
        .filter(
            RecipeRatingHistories.period_type == period_enum,
            RecipeRatingHistories.period_start_date == period_start_date,
            RecipeRatingHistories.rating_count > 0,
        )
        .order_by(desc(avg_rating_expr))
        .limit(10)
        .all()
    )
    return {"recipes": [
        {
            "id": recipe.id,
            "name": recipe.name,
            "image_url": recipe.image_url,
            "avg_rating": float(hist.rating_sum / hist.rating_count),
            "rating_count": hist.rating_count,
            "view_count": recipe.view_count or 0,
        }
        for recipe, hist in rankings
    ]}


# ---------------------------------
# BMI 기반 추천
# ---------------------------------
@router.get("/recommendations/bmi")
def get_bmi_recommendations(user_id: str = Query(...), db: Session = Depends(get_db)):
    user_profile = db.query(UserDetail).filter_by(user_id=user_id).first()
    if not user_profile or not user_profile.height or not user_profile.weight:
        raise HTTPException(400, "사용자 신체 정보 필요")

    bmi = float(user_profile.weight) / ((float(user_profile.height) / 100) ** 2)
    bmi_class = classify_bmi(bmi)

    if bmi_class == "저체중":
        query = db.query(Recipe).filter(Recipe.category.in_(["밥", "구이, 찜"])).order_by(Recipe.INFO_ENG.desc())
    elif bmi_class == "정상":
        query = db.query(Recipe).order_by(Recipe.view_count.desc())
    elif bmi_class == "과체중":
        query = db.query(Recipe).filter(Recipe.category.in_(["샐러드", "국, 찌개", "반찬"])).order_by(Recipe.INFO_ENG.asc())
    else:
        query = db.query(Recipe).filter(Recipe.category.in_(["샐러드", "반찬"])).order_by(Recipe.INFO_ENG.asc())

    recipes = query.limit(10).all()
    return {
        "bmi": round(bmi, 2),
        "bmi_category": bmi_class,
        "recipes": [{
            "id": r.id,
            "name": r.name,
            "image_url": r.image_url,
            "category": r.category,
            "avg_rating": float(r.avg_rating or 0),
            "rating_count": r.rating_count or 0,
            "view_count": r.view_count or 0,
        } for r in recipes]
    }


# ---------------------------------
# 이미지 업로드 & 분석
# ---------------------------------
@router.post("/recipes/upload")
async def upload_recipe_image(image: UploadFile = File(...), db: Session = Depends(get_db)):
    upload_dir = "temp_uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, image.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    except Exception as e:
        raise HTTPException(500, f"파일 저장 실패: {str(e)}")

    try:
        results = model(file_path)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(500, f"YOLO 추론 실패: {str(e)}")

    food_names = []
    for r in results:
        if hasattr(r, "boxes"):
            for box in r.boxes:
                label = model.names[int(box.cls[0])]
                food_names.append(label)
    os.remove(file_path)

    if not food_names:
        raise HTTPException(404, "이미지에서 음식을 인식하지 못했습니다.")

    search_name = Counter(food_names).most_common(1)[0][0].split("_", 1)[-1]
    recipes = service.get_recipe(search_name, db)
    if not recipes:
        raise HTTPException(404, f"{search_name} 기반 검색 결과 없음")
    return recipes


# ---------------------------------
# 사용자 선호 기반 추천
# ---------------------------------
@router.get("/recommendations/user-preferences")
def get_user_preference_recommendations(user_id: str = Query(...), db: Session = Depends(get_db)):
    recent_searches = (
        db.query(UserSearchHistory.search_word)
        .filter(UserSearchHistory.user_id == user_id)
        .order_by(UserSearchHistory.search_time.desc())
        .limit(5)
        .all()
    )
    keywords = [kw for (kw,) in recent_searches]
    if not keywords:
        return {"recipes": []}

    categories = [c for (c,) in db.query(distinct(Recipe.category)).filter(
        or_(*[Recipe.name.ilike(f"%{kw}%") for kw in keywords])
    ).all()]
    if not categories:
        return {"recipes": []}

    recipes = db.query(Recipe).filter(Recipe.category.in_(categories)).order_by(Recipe.view_count.desc()).limit(10).all()
    if len(recipes) < 10:
        needed = 10 - len(recipes)
        extra = db.query(Recipe).filter(~Recipe.id.in_([r.id for r in recipes])
        ).order_by(Recipe.view_count.desc()).limit(needed).all()
        recipes.extend(extra)

    return {"recipes": [{
        "id": r.id,
        "name": r.name,
        "image_url": r.image_url,
        "category": r.category,
        "avg_rating": float(r.avg_rating or 0),
        "rating_count": r.rating_count or 0,
        "view_count": r.view_count or 0,
    } for r in recipes]}


# ---------------------------------
# 검색 기록 저장/조회
# ---------------------------------
@router.post("/search-history")
def add_search_history(request: SearchHistoryRequest, db: Session = Depends(get_db)):
    history = UserSearchHistory(
        user_id=request.user_id,
        recipe_id=request.recipe_id,
        search_word=request.search_word,
        search_time=datetime.now()
    )
    db.add(history)
    db.commit()
    return {"message": "Search history saved"}


@router.get("/search-history/{user_id}")
def get_search_history(user_id: str, page: int = 1, items_per_page: int = 10, db: Session = Depends(get_db)):
    offset = (page - 1) * items_per_page
    total_count = db.query(UserSearchHistory).filter(UserSearchHistory.user_id == user_id).count()
    histories = db.query(UserSearchHistory).filter(
        UserSearchHistory.user_id == user_id
    ).order_by(UserSearchHistory.search_time.desc()).offset(offset).limit(items_per_page).all()

    return {
        "totalCount": total_count,
        "histories": [
            {
                "id": h.id,
                "user_id": h.user_id,
                "recipe_id": h.recipe_id,
                "search_word": h.search_word,
                "search_time": h.search_time.isoformat() if h.search_time else None
            }
            for h in histories
        ]
    }


# ---------------------------------
# 페이징 레시피 조회
# ---------------------------------
@router.get("/recipes")
def get_recipes(category: str = Query(None), search: str = Query(None), page: int = Query(1), db: Session = Depends(get_db)):
    query = db.query(Recipe)
    if category and category != "전체":
        query = query.filter(Recipe.category == category)
    if search:
        query = query.filter(Recipe.name.contains(search))

    total_count = query.count()
    page_size = 12
    recipes = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "recipes": [{
            "id": r.id,
            "name": r.name,
            "image_url": r.image_url,
            "category": r.category,
            "avg_rating": float(r.avg_rating or 0),
            "rating_count": r.rating_count or 0,
            "view_count": r.view_count or 0,
        } for r in recipes],
        "total_count": total_count
    }





# 정용우 시작



class ChatRequest(BaseModel):
    message: str

# ✅ 완성형: ask_chatbot 사용
@router.post("/chatbot")
def chatbot_answer(request: ChatRequest):
    try:
        answer = ask_chatbot(request.message)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ 스트리밍: text/plain 스트림
@router.post("/chatbot/stream")
def chatbot_stream(request: ChatRequest):
    prompt = (
        f"'{request.message}'에 대해 요리 전문가처럼 자세하고 친절하게 요리 레시피를 단계별로 설명해줘. "
        f"칼로리,지방 같은 영양성분과 재료를 먼저 알려줘. "
        f"그 다음에는 1단계,2단계...단계별로 요리 순서를 알려줘"
    )
    def token_stream():
        try:
            response = gemini_model.generate_content(prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"\n[ERROR] {str(e)}"

    return StreamingResponse(token_stream(), media_type="text/plain; charset=utf-8")



# 정용우 끝
    
    