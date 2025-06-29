from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api.api_v1.api import api_router
from app.core.config import settings
import uvicorn
import logging
import time
import traceback
from typing import Dict, Any

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="GomGom Recipe API",
    description="레시피 추천 및 검색 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    # 성능 최적화 설정
    openapi_url="/openapi.json",
    # 비동기 지원 강화
    default_response_class=JSONResponse,
)

# Gzip 압축 미들웨어 추가 (응답 크기 감소)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS 설정 (더 구체적으로 설정)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:3000",  
#         "http://localhost:3001",
#         "http://127.0.0.1:3000",
#         "http://127.0.0.1:3001",
#         "*"  
#     ],
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#     allow_headers=["*"],
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 요청 로깅 미들웨어
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """모든 요청을 로깅하는 미들웨어"""
    start_time = time.time()
    
    # 요청 정보 로깅
    logger.info(f"요청 시작: {request.method} {request.url.path} - {request.client.host}")
    
    try:
        response = await call_next(request)
        
        # 응답 시간 계산
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # 응답 정보 로깅
        logger.info(f"요청 완료: {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")
        
        return response
    
    except Exception as e:
        # 오류 발생 시 로깅
        process_time = time.time() - start_time
        logger.error(f"요청 실패: {request.method} {request.url.path} - {str(e)} ({process_time:.3f}s)")
        logger.error(f"오류 상세: {traceback.format_exc()}")
        raise

# 전역 예외 처리기
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP 예외 처리"""
    logger.error(f"HTTP 예외 발생: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP 오류",
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """요청 검증 오류 처리"""
    logger.error(f"요청 검증 오류: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "요청 데이터 검증 오류",
            "detail": exc.errors(),
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """일반 예외 처리"""
    logger.error(f"예상치 못한 오류 발생: {str(exc)}")
    logger.error(f"오류 상세: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "서버 내부 오류",
            "detail": "예상치 못한 오류가 발생했습니다.",
            "path": request.url.path
        }
    )

# 라우터 등록
app.include_router(api_router, prefix="/api/v1")

# 루트 경로 엔드포인트
@app.get("/")
async def root():
    """API 루트 경로 - 기본 정보 반환"""
    return {
        "message": "GomGom Recipe API에 오신 것을 환영합니다!",
        "version": "1.0.0",
        "description": "레시피 추천 및 검색 API",
        "endpoints": {
            "health_check": "/health",
            "api_docs": "/docs",
            "api_redoc": "/redoc",
            "api_v1": "/api/v1"
        },
        "status": "running"
    }

# 헬스체크 엔드포인트
@app.get("/health")
async def health_check():
    """애플리케이션 상태 확인"""
    try:
        # 서비스 상태 확인
        health_status = {
            "status": "healthy",
            "message": "GomGom Recipe API is running",
            "version": "1.0.0",
            "timestamp": time.time(),
            "services": {}
        }
        
        # 데이터베이스 상태 확인
        try:
            from app.db.session import SessionLocal
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
            health_status["services"]["database"] = "connected"
        except Exception as e:
            logger.error(f"데이터베이스 상태 확인 실패: {e}")
            health_status["services"]["database"] = "disconnected"
            health_status["status"] = "degraded"
        
        # Redis 상태 확인
        try:
            from app.core.cache import Cache
            cache = Cache()
            if cache.redis_client:
                cache.redis_client.ping()
                health_status["services"]["redis"] = "connected"
            else:
                health_status["services"]["redis"] = "disabled"
        except Exception as e:
            logger.error(f"Redis 상태 확인 실패: {e}")
            health_status["services"]["redis"] = "disconnected"
        
        # API 키 상태 확인
        api_keys_status = {}
        if settings.OPENAI_API_KEY:
            api_keys_status["openai"] = "configured"
        else:
            api_keys_status["openai"] = "missing"
            health_status["status"] = "degraded"
        
        if settings.SPOONACULAR_API_KEY:
            api_keys_status["spoonacular"] = "configured"
        else:
            api_keys_status["spoonacular"] = "missing"
            health_status["status"] = "degraded"
        
        health_status["api_keys"] = api_keys_status
        
        logger.info("헬스체크 요청 처리 완료")
        return health_status
    
    except Exception as e:
        logger.error(f"헬스체크 중 오류 발생: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": "서버 상태 확인 중 오류가 발생했습니다.",
                "detail": str(e)
            }
        )

# 서버 시작 설정 (성능 최적화)
if __name__ == "__main__":
    try:
        logger.info("GomGom Recipe API 서버 시작 중...")
        
        # 시작 전 초기화 검증
        logger.info("서비스 초기화 검증 중...")
        
        # 설정 검증
        if not settings.OPENAI_API_KEY:
            logger.warning("⚠️  OPENAI_API_KEY가 설정되지 않았습니다. AI 기능이 제한됩니다.")
        
        if not settings.SPOONACULAR_API_KEY:
            logger.warning("⚠️  SPOONACULAR_API_KEY가 설정되지 않았습니다. 레시피 검색 기능이 제한됩니다.")
        
        # 데이터베이스 연결 테스트
        try:
            from app.db.session import SessionLocal
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
            logger.info("✅ 데이터베이스 연결 확인 완료")
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 실패: {e}")
            logger.warning("데이터베이스 없이 서버를 시작합니다. 일부 기능이 제한됩니다.")
        
        # Redis 연결 테스트
        try:
            from app.core.cache import Cache
            cache = Cache()
            if cache.redis_client:
                cache.redis_client.ping()
                logger.info("✅ Redis 연결 확인 완료")
            else:
                logger.warning("⚠️  Redis가 비활성화되어 있습니다.")
        except Exception as e:
            logger.error(f"❌ Redis 연결 실패: {e}")
            logger.warning("Redis 없이 서버를 시작합니다. 캐시 기능이 비활성화됩니다.")
        
        logger.info("🚀 서버 시작 준비 완료")
        
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,  # 개발 중 자동 재시작
            workers=1,    # 단일 워커 (개발 환경)
            loop="asyncio",
            # 성능 최적화 옵션
            access_log=True,
            log_level="info",
            # 연결 최적화
            limit_concurrency=1000,
            limit_max_requests=10000,
            timeout_keep_alive=30,
        )
    except Exception as e:
        logger.error(f"서버 시작 실패: {e}")
        raise 