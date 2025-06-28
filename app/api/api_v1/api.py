from fastapi import APIRouter
from app.api.api_v1.endpoints import recipes, recommendations, location, auth, ingredients, restaurants, recommend_result, test_result, translate

api_router = APIRouter()

# 레시피 관련 엔드포인트
api_router.include_router(
    recipes.router,
    prefix="/recipes",
    tags=["recipes"],
    responses={
        404: {"description": "Recipe not found"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    }
)

# 추천 관련 엔드포인트
api_router.include_router(
    recommendations.router,
    prefix="/recommendations",
    tags=["recommendations"],
    responses={
        404: {"description": "Recommendation not found"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    }
)

# 위치 정보 관련 엔드포인트
api_router.include_router(
    location.router,
    prefix="/locations",
    tags=["locations"],
    responses={
        404: {"description": "Location not found"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    }
)

# 인증 관련 엔드포인트
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
    responses={
        401: {"description": "Unauthorized"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    }
)

# 재료 관련 엔드포인트
api_router.include_router(
    ingredients.router,
    prefix="/ingredients",
    tags=["ingredients"],
    responses={
        404: {"description": "Ingredient not found"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    }
)

# 추천 결과 관련 엔드포인트
api_router.include_router(
    recommend_result.router,
    prefix="/recommend_result",
    tags=["recommend_result"],
    responses={
        404: {"description": "Recommend result not found"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    }
)

# 음식점 관련 엔드포인트
api_router.include_router(
    restaurants.router,
    prefix="",
    tags=["restaurants"],
    responses={
        404: {"description": "Restaurant not found"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    }
)

# 테스트 결과 관련 엔드포인트
api_router.include_router(
    test_result.router,
    prefix="",
    tags=["test_result"],
    responses={
        404: {"description": "Test result not found"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    }
)

# 번역 관련 엔드포인트
api_router.include_router(
    translate.router,
    prefix="",
    tags=["translate"],
    responses={
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    }
) 