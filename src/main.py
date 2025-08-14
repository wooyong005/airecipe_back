# main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from recipe.router import router as recipe_router
from user.router import router as user_router

from ai.ai_model import model  # 위에서 만든 모듈에서 모델 임포트


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 프론트 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# FastAPI 의존성으로 모델 객체 제공
def get_model():
    return model


# 라우터 등록 시 prefix 유지
app.include_router(recipe_router, prefix="/api")
app.include_router(user_router, prefix="/api/users")
