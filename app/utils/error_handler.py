import logging
from typing import Any, Callable, Optional
from functools import wraps
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import traceback

logger = logging.getLogger(__name__)

def handle_database_errors(func: Callable) -> Callable:
    """데이터베이스 오류를 처리하는 데코레이터"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except IntegrityError as e:
            logger.error(f"데이터 무결성 오류 ({func.__name__}): {e}")
            raise HTTPException(status_code=400, detail="잘못된 데이터입니다.")
        except SQLAlchemyError as e:
            logger.error(f"데이터베이스 오류 ({func.__name__}): {e}")
            raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다.")
        except Exception as e:
            logger.error(f"예상치 못한 오류 ({func.__name__}): {e}")
            logger.error(f"오류 상세: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")
    return wrapper

def handle_api_errors(func: Callable) -> Callable:
    """API 오류를 처리하는 데코레이터"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            raise
        except ValueError as e:
            logger.error(f"매개변수 검증 오류 ({func.__name__}): {e}")
            raise HTTPException(status_code=422, detail=f"매개변수 검증 오류: {str(e)}")
        except Exception as e:
            logger.error(f"API 오류 ({func.__name__}): {e}")
            logger.error(f"오류 상세: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")
    return wrapper

def safe_execute(func: Callable, *args, **kwargs) -> Optional[Any]:
    """안전한 함수 실행 (동기)"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"함수 실행 오류 ({func.__name__}): {e}")
        return None

async def safe_execute_async(func: Callable, *args, **kwargs) -> Optional[Any]:
    """안전한 비동기 함수 실행"""
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        logger.error(f"비동기 함수 실행 오류 ({func.__name__}): {e}")
        return None

def validate_coordinates(lat: float, lng: float) -> bool:
    """좌표 유효성 검증"""
    if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
        return False
    return True

def validate_pagination_params(skip: int, limit: int) -> bool:
    """페이지네이션 매개변수 검증"""
    if skip < 0 or limit < 1 or limit > 1000:
        return False
    return True

def log_api_request(method: str, path: str, status_code: int, duration: float):
    """API 요청 로깅"""
    if status_code >= 400:
        logger.warning(f"API 요청 실패: {method} {path} - {status_code} ({duration:.3f}s)")
    else:
        # logger.info(f"API 요청 성공: {method} {path} - {status_code} ({duration:.3f}s)")
        pass

def log_database_operation(operation: str, table: str, success: bool, error: Optional[str] = None):
    """데이터베이스 작업 로깅"""
    if success:
        logger.debug(f"DB 작업 성공: {operation} on {table}")
    else:
        logger.error(f"DB 작업 실패: {operation} on {table} - {error}")

def create_error_response(error_type: str, message: str, details: Optional[Any] = None) -> dict:
    """표준 오류 응답 생성"""
    response = {
        "error": error_type,
        "message": message
    }
    if details:
        response["details"] = details
    return response 