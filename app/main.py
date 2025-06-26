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
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js 개발 서버
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "*"  # 개발 중에는 모든 origin 허용
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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

# 헬스체크 엔드포인트
@app.get("/health")
async def health_check():
    """애플리케이션 상태 확인"""
    try:
        # 기본 상태 정보
        health_info = {
            "status": "healthy",
            "message": "GomGom Recipe API is running",
            "version": "1.0.0",
            "timestamp": time.time()
        }
        
        logger.info("헬스체크 요청 처리 완료")
        return health_info
    
    except Exception as e:
        logger.error(f"헬스체크 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="서버 상태 확인 중 오류가 발생했습니다.")

# 서버 시작 설정 (성능 최적화)
if __name__ == "__main__":
    try:
        logger.info("GomGom Recipe API 서버 시작 중...")
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