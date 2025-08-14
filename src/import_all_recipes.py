# from service.recipe_service import fetch_and_save_all_recipes 
from recipe.service import fetch_and_save_all_recipes # 위 처럼 돼 있어서 모듈을 불러오지 않아 수정함 # 정용우
from database import SessionLocal 

if __name__ == "__main__":
    with SessionLocal() as db:
        fetch_and_save_all_recipes(db, total=10000, batch_size=500)
    print("전체 레시피 적재 완료!")
