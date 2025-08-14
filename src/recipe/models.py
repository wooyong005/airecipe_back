from sqlalchemy import (
    Column, Integer, String, Text, DECIMAL, DateTime, ForeignKey, Enum, Date
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from base import Base  # src/base.py에 선언한 Base 사용

# ----------- Enum 정의 ----------
class PeriodTypeEnum(enum.Enum):
    daily = 'daily'
    weekly = 'weekly'
    monthly = 'monthly'


# ----------- Recipe 테이블 ----------
class Recipe(Base):
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True)  # 외부 API의 RCP_SEQ
    name = Column(String(255), nullable=False)
    description = Column(Text)
    image_url = Column(String(255))
    view_count = Column(Integer, default=0)
    avg_rating = Column(DECIMAL(3, 2), default=0)
    rating_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    category = Column(String(50))
    ingredients = Column(Text)
    INFO_ENG = Column(String(20))
    INFO_CAR = Column(String(20))
    INFO_PRO = Column(String(20))
    INFO_FAT = Column(String(20))
    INFO_NA = Column(String(20))
    RCP_NA_TIP = Column(Text)

    MANUAL01 = Column(Text)
    MANUAL02 = Column(Text)
    MANUAL03 = Column(Text)
    MANUAL04 = Column(Text)
    MANUAL05 = Column(Text)
    MANUAL06 = Column(Text)
    MANUAL07 = Column(Text)
    MANUAL08 = Column(Text)
    MANUAL09 = Column(Text)
    MANUAL10 = Column(Text)
    MANUAL11 = Column(Text)
    MANUAL12 = Column(Text)
    MANUAL13 = Column(Text)
    MANUAL14 = Column(Text)
    MANUAL15 = Column(Text)
    MANUAL16 = Column(Text)
    MANUAL17 = Column(Text)
    MANUAL18 = Column(Text)
    MANUAL19 = Column(Text)
    MANUAL20 = Column(Text)

    MANUAL_IMG01 = Column(String(255))
    MANUAL_IMG02 = Column(String(255))
    MANUAL_IMG03 = Column(String(255))
    MANUAL_IMG04 = Column(String(255))
    MANUAL_IMG05 = Column(String(255))
    MANUAL_IMG06 = Column(String(255))
    MANUAL_IMG07 = Column(String(255))
    MANUAL_IMG08 = Column(String(255))
    MANUAL_IMG09 = Column(String(255))
    MANUAL_IMG10 = Column(String(255))
    MANUAL_IMG11 = Column(String(255))
    MANUAL_IMG12 = Column(String(255))
    MANUAL_IMG13 = Column(String(255))
    MANUAL_IMG14 = Column(String(255))
    MANUAL_IMG15 = Column(String(255))
    MANUAL_IMG16 = Column(String(255))
    MANUAL_IMG17 = Column(String(255))
    MANUAL_IMG18 = Column(String(255))
    MANUAL_IMG19 = Column(String(255))
    MANUAL_IMG20 = Column(String(255))

    # 관계 설정
    ratings = relationship("Rating", back_populates="recipe", cascade="all, delete-orphan")
    rating_histories = relationship("RecipeRatingHistories", back_populates="recipe", cascade="all, delete-orphan")
    view_count_histories = relationship("RecipeViewCountHistories", back_populates="recipe", cascade="all, delete-orphan")
    favorited_by = relationship("UserFavorites", back_populates="recipe", cascade="all, delete-orphan")


# ----------- Rating 테이블 ----------
class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(String(50), ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    rating = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    recipe = relationship("Recipe", back_populates="ratings")
    user = relationship("User", back_populates="ratings")


# ----------- RecipeRatingHistories 테이블 ----------
class RecipeRatingHistories(Base):
    __tablename__ = 'recipe_rating_histories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False)
    period_type = Column(Enum(PeriodTypeEnum), nullable=False)
    period_start_date = Column(Date, nullable=False)
    rating_sum = Column(Integer, default=0, nullable=False)
    rating_count = Column(Integer, default=0, nullable=False)
    avg_rating = Column(DECIMAL(3, 2))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    recipe = relationship("Recipe", back_populates="rating_histories")


# ----------- RecipeViewCountHistories 테이블 ----------
class RecipeViewCountHistories(Base):
    __tablename__ = 'recipe_view_count_histories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False)
    date = Column(Date, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    recipe = relationship("Recipe", back_populates="view_count_histories")
