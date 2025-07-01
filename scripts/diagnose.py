#!/usr/bin/env python3
"""
GomGom AI 서비스 진단 스크립트
KOE006 오류 및 기타 설정 문제를 진단합니다.
"""

import os
import sys
import subprocess
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

def print_header(title):
    # Print(f"\n{'='*50}")
    # Print(f"🔍 {title}")
    # Print(f"{'='*50}")

def print_section(title):
    # Print(f"\n📋 {title}")
    print("-" * 30)

def check_env_file():
    """환경 변수 파일 확인"""
    print_section("환경 변수 파일 확인")
    
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env 파일이 존재합니다.")
        
        # 환경 변수 로드
        load_dotenv()
        
        # 필수 환경 변수 확인
        required_vars = [
            "OPENAI_API_KEY",
            "SPOONACULAR_API_KEY",
            "POSTGRES_HOST",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "POSTGRES_DB",
            "KAKAO_REST_API",
            "KAKAO_CLIENT_ID"
        ]
        
        for var in required_vars:
            value = os.getenv(var)
            if value and value not in ["your_openai_api_key_here", "your_spoonacular_api_key_here"]:
                # Print(f"✅ {var}: 설정됨")
            else:
                # Print(f"❌ {var}: 설정되지 않음 또는 기본값")
    else:
        print("❌ .env 파일이 없습니다.")
        print("💡 해결방법: cp env.example .env")

def check_database_connection():
    """데이터베이스 연결 확인"""
    print_section("데이터베이스 연결 확인")
    
    try:
        import psycopg2
        from psycopg2 import OperationalError
        
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        database = os.getenv("POSTGRES_DB", "gomgomdb")
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "postgres1234")
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        conn.close()
        print("✅ PostgreSQL 데이터베이스 연결 성공")
        
    except ImportError:
        print("❌ psycopg2가 설치되지 않았습니다.")
        print("💡 해결방법: pip install psycopg2-binary")
    except OperationalError as e:
        # Print(f"❌ 데이터베이스 연결 실패: {e}")
        print("💡 해결방법: PostgreSQL 서버가 실행 중인지 확인하세요.")

def check_redis_connection():
    """Redis 연결 확인"""
    print_section("Redis 연결 확인")
    
    try:
        import redis
        
        host = os.getenv("REDIS_HOST", "127.0.0.1")
        port = int(os.getenv("REDIS_PORT", "6379"))
        db = int(os.getenv("REDIS_DB", "1"))
        
        redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        redis_client.ping()
        print("✅ Redis 연결 성공")
        
    except ImportError:
        print("❌ redis가 설치되지 않았습니다.")
        print("💡 해결방법: pip install redis")
    except Exception as e:
        # Print(f"❌ Redis 연결 실패: {e}")
        print("💡 해결방법: Redis 서버가 실행 중인지 확인하세요.")

def check_api_keys():
    """API 키 유효성 확인"""
    print_section("API 키 확인")
    
    # OpenAI API 키 확인
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key != "your_openai_api_key_here":
        print("✅ OpenAI API 키가 설정되어 있습니다.")
    else:
        print("❌ OpenAI API 키가 설정되지 않았습니다.")
    
    # Spoonacular API 키 확인
    spoonacular_key = os.getenv("SPOONACULAR_API_KEY")
    if spoonacular_key and spoonacular_key != "your_spoonacular_api_key_here":
        print("✅ Spoonacular API 키가 설정되어 있습니다.")
    else:
        print("❌ Spoonacular API 키가 설정되지 않았습니다.")
    
    # Kakao API 키 확인
    kakao_key = os.getenv("KAKAO_REST_API")
    if kakao_key:
        print("✅ Kakao API 키가 설정되어 있습니다.")
    else:
        print("❌ Kakao API 키가 설정되지 않았습니다.")

def check_server_status():
    """서버 상태 확인"""
    print_section("서버 상태 확인")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ FastAPI 서버가 실행 중입니다.")
            # Print(f"   상태: {data.get('status', 'unknown')}")
            
            # 서비스 상태 출력
            services = data.get('services', {})
            for service, status in services.items():
                # Print(f"   {service}: {status}")
                
        else:
            # Print(f"❌ 서버 응답 오류: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ FastAPI 서버에 연결할 수 없습니다.")
        print("💡 해결방법: 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        # Print(f"❌ 서버 상태 확인 실패: {e}")

def check_frontend():
    """프론트엔드 상태 확인"""
    print_section("프론트엔드 상태 확인")
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Next.js 프론트엔드가 실행 중입니다.")
        else:
            # Print(f"❌ 프론트엔드 응답 오류: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Next.js 프론트엔드에 연결할 수 없습니다.")
        print("💡 해결방법: npm run dev로 프론트엔드를 시작하세요.")
    except Exception as e:
        # Print(f"❌ 프론트엔드 상태 확인 실패: {e}")

def check_pm2_status():
    """PM2 상태 확인"""
    print_section("PM2 상태 확인")
    
    try:
        result = subprocess.run(["pm2", "status"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PM2가 설치되어 있습니다.")
            print(result.stdout)
        else:
            print("❌ PM2 명령어 실행 실패")
    except FileNotFoundError:
        print("❌ PM2가 설치되지 않았습니다.")
        print("💡 해결방법: npm install -g pm2")

def generate_report():
    """진단 보고서 생성"""
    print_header("진단 보고서")
    
    check_env_file()
    check_database_connection()
    check_redis_connection()
    check_api_keys()
    check_server_status()
    check_frontend()
    check_pm2_status()
    
    print_header("KOE006 오류 해결 방법")
    print("""
KOE006 오류는 일반적으로 다음과 같은 원인으로 발생합니다:

1. 환경 변수 설정 문제
   - .env 파일이 없거나 잘못 설정됨
   - 필수 API 키가 누락됨

2. 데이터베이스 연결 문제
   - PostgreSQL 서버가 실행되지 않음
   - 데이터베이스 접속 정보가 잘못됨

3. Redis 연결 문제
   - Redis 서버가 실행되지 않음
   - Redis 접속 정보가 잘못됨

4. 서버 실행 문제
   - FastAPI 서버가 실행되지 않음
   - 포트 충돌

해결 방법:
1. .env 파일을 생성하고 올바른 값으로 설정
2. 데이터베이스와 Redis 서버 시작
3. ./start_server.sh 실행
4. npm run dev로 프론트엔드 시작
    """)

if __name__ == "__main__":
    generate_report() 