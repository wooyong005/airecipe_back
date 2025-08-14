from pydantic import BaseModel

# 평점 입력용 Pydantic 모델
class RatingRequest(BaseModel):
    user_id: str
    rating: int

# 즐겨찾기(찜) 관련 Pydantic 모델 추가
class FavoriteRequest(BaseModel):
    user_id: str
    recipe_id: int

# 사용자 검색 이력 저장용 Pydantic 모델
class SearchHistoryRequest(BaseModel):
    user_id: str
    recipe_id: int = None
    search_word: str

# 사용자 검색 이력 응답용 Pydantic 모델
class SearchHistoryResponse(BaseModel):
    id: int
    user_id: str
    search_word: str
    search_time: str
class Config:
    from_attributes = True

# BMI 저장용 Pydantic 모델
class BmiRecommendationRequest(BaseModel):
    user_id: str
    height: float
    weight: float
    recommended_recipes: str = None