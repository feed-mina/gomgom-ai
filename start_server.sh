#!/bin/bash

echo "🚀 GomGom AI 서버 시작 스크립트"
echo "================================"

# 백엔드 디렉토리로 이동
cd /home/ubuntu/backend

# 환경 변수 파일 확인
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다. env.example을 복사하여 .env 파일을 생성하세요."
    echo "cp env.example .env"
    echo "그 후 .env 파일에서 실제 값으로 변경하세요."
    exit 1
fi

# PM2 프로세스 중지
echo "🛑 기존 PM2 프로세스 중지 중..."
pm2 stop gomgom-ai 2>/dev/null || echo "기존 프로세스가 없습니다."
pm2 delete gomgom-ai 2>/dev/null || echo "기존 프로세스가 없습니다."

# 환경 변수 로드
echo "📋 환경 변수 로드 중..."
source .env

# 필수 환경 변수 검증
echo "🔍 환경 변수 검증 중..."

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "⚠️  경고: OPENAI_API_KEY가 설정되지 않았습니다. AI 기능이 제한됩니다."
fi

if [ -z "$SPOONACULAR_API_KEY" ] || [ "$SPOONACULAR_API_KEY" = "your_spoonacular_api_key_here" ]; then
    echo "⚠️  경고: SPOONACULAR_API_KEY가 설정되지 않았습니다. 레시피 검색 기능이 제한됩니다."
fi

# 데이터베이스 연결 테스트
echo "🗄️  데이터베이스 연결 테스트 중..."
if command -v psql &> /dev/null; then
    if PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1;" &> /dev/null; then
        echo "✅ 데이터베이스 연결 성공"
    else
        echo "❌ 데이터베이스 연결 실패"
        echo "데이터베이스가 실행 중인지 확인하세요."
    fi
else
    echo "⚠️  psql 명령어를 찾을 수 없습니다. 데이터베이스 연결을 수동으로 확인하세요."
fi

# Redis 연결 테스트
echo "🔴 Redis 연결 테스트 중..."
if command -v redis-cli &> /dev/null; then
    if redis-cli -h $REDIS_HOST -p $REDIS_PORT ping &> /dev/null; then
        echo "✅ Redis 연결 성공"
    else
        echo "❌ Redis 연결 실패"
        echo "Redis가 실행 중인지 확인하세요."
    fi
else
    echo "⚠️  redis-cli 명령어를 찾을 수 없습니다. Redis 연결을 수동으로 확인하세요."
fi

# 프론트엔드 빌드
echo "🎨 프론트엔드 빌드 중..."
cd /home/ubuntu/frontend
npm install
npm run build
cd /home/ubuntu/backend

# PM2로 애플리케이션 시작
echo "🚀 PM2로 애플리케이션 시작 중..."
pm2 start ecosystem.config.js

# 상태 확인
echo "📊 PM2 상태 확인 중..."
pm2 status

echo ""
echo "✅ 서버 시작 완료!"
echo "📝 로그 확인: pm2 logs gomgom-ai"
echo "🛑 서버 중지: pm2 stop gomgom-ai"
echo "🔄 서버 재시작: pm2 restart gomgom-ai" 