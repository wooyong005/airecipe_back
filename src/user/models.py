from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from base import Base  # src/base.py 또는 공용 Base import

# ----------- User 테이블 ----------
class User(Base):
    __tablename__ = 'user'

    user_id = Column(String(50), primary_key=True)
    pw = Column(String(255), nullable=False)
    ko_name = Column(String(30))
    email = Column(String(100))

    user_detail = relationship("UserDetail", uselist=False, back_populates="user", cascade="all, delete-orphan")
    bmi_recommendations = relationship("UserBmiRecommendation", back_populates="user", cascade="all, delete-orphan")
    search_histories = relationship("UserSearchHistory", back_populates="user", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("UserFavorites", back_populates="user", cascade="all, delete-orphan")


# ----------- UserDetail ----------
class UserDetail(Base):
    __tablename__ = 'user_detail'
    user_id = Column(String(50), ForeignKey('user.user_id', ondelete='CASCADE'), primary_key=True)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    preferred_food = Column(String(100), nullable=True)
    preferred_tags = Column(String(200), nullable=True)
    birth_date = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship("User", back_populates="user_detail")


# ----------- UserSearchHistory ----------
class UserSearchHistory(Base):
    __tablename__ = 'user_search_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    recipe_id = Column(Integer, ForeignKey('recipes.id', ondelete='CASCADE'), nullable=True)
    search_word = Column(String(255), nullable=False)
    search_time = Column(DateTime, default=datetime.now, nullable=False)

    user = relationship("User", back_populates="search_histories")


# ----------- UserBmiRecommendation ----------
class UserBmiRecommendation(Base):
    __tablename__ = 'user_bmi_recommendation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    bmi_value = Column(Float, nullable=False)
    recommended_at = Column(DateTime, default=datetime.now, nullable=False)
    recommended_recipes = Column(Text, nullable=True)

    user = relationship("User", back_populates="bmi_recommendations")


# ----------- UserFavorites ----------
class UserFavorites(Base):
    __tablename__ = 'user_favorites'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    recipe_id = Column(Integer, ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    user = relationship("User", back_populates="favorites")
    recipe = relationship("Recipe", back_populates="favorited_by")

    __table_args__ = (
        UniqueConstraint('user_id', 'recipe_id', name='unique_user_recipe_favorite'),
    )
