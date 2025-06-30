from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Text, DECIMAL
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    recommendations = relationship("Recommendation", back_populates="user")

    def __repr__(self):
        return f"<User {self.email}>"

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    instructions = Column(Text)
    cooking_time = Column(Integer)
    difficulty = Column(String)
    servings = Column(Integer, default=1)
    image_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    recommendations = relationship("Recommendation", back_populates="recipe")

    def __repr__(self):
        return f"<Recipe {self.name}>"

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(DECIMAL(10, 2))
    unit = Column(String)
    category = Column(String)
    image_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    korean_names = relationship("IngredientKorean", back_populates="ingredient")

    def __repr__(self):
        return f"<Ingredient {self.name}>"

class IngredientKorean(Base):
    __tablename__ = "ingredients_ko"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ingredient = relationship("Ingredient", back_populates="korean_names")

    def __repr__(self):
        return f"<IngredientKorean {self.name}>"

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    phone = Column(String)
    website = Column(String)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Location {self.name}>"

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    score = Column(DECIMAL(3, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="recommendations")
    recipe = relationship("Recipe", back_populates="recommendations")

    def __repr__(self):
        return f"<Recommendation {self.user_id} -> {self.recipe_id}>"

class RecommendationHistory(Base):
    __tablename__ = "recommendation_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 로그인하지 않은 사용자도 허용
    request_type = Column(String(32), nullable=False)  # test_result, recommend_result, search_recipe
    input_data = Column(JSONB, nullable=False)  # 입력 데이터 (쿼리, 위치 등)
    result_data = Column(JSONB, nullable=False)  # 추천 결과 데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", backref="recommendation_history")

    def __repr__(self):
        return f"<RecommendationHistory {self.request_type} - {self.created_at}>" 