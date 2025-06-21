#!/bin/bash

# PM2 프로세스 중지
pm2 stop gomgom-ai
pm2 delete gomgom-ai

# 환경 변수 설정 (실제 값으로 변경 필요)
export OPENAI_API_KEY="your_openai_api_key_here"
export POSTGRES_SERVER="localhost"
export POSTGRES_USER="postgres"
export POSTGRES_PASSWORD="postgres1234"
export POSTGRES_DB="gomgomdb"
export POSTGRES_PORT="5432"
export POSTGRES_HOST="localhost"
export REDIS_HOST="127.0.0.1"
export REDIS_PORT="6379"
export REDIS_DB="1"
export REDIS_URL="redis://localhost:6379"
export SECRET_KEY="django-insecure-k3=p4i=(mu-)*2w4d6-_)3h+w(o&sk5*tl)c-#n^%7(!w6co8@"
export JWT_SECRET_KEY="d6ac9ecc0a3aa3c395313fb236e0ec10d71ab78fb36f54ba626664eba0b842b1"
export JWT_ISSUER="admin"
export ACCESS_TOKEN_EXPIRE_MINUTES="30"
export KAKAO_REST_API="ce290686267085588527fc7c5b9334b3"
export KAKAO_CLIENT_ID="2d22c7fa1d59eb77a5162a3948a0b6fe"
export KAKAO_TOKEN_ADMIN="96ed9105639fb627fb2c710f39e6516f"
export KAKAO_REDIRECT_URI="http://localhost:4000/oauth/callback"
export CACHE_ENABLED="true"
export LOG_LEVEL="INFO"
export NEXT_PUBLIC_API_URL="http://localhost:8000"

# PM2로 애플리케이션 시작
pm2 start ecosystem.config.js

# 상태 확인
pm2 status 