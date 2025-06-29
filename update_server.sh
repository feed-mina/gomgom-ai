#!/bin/bash

echo "🔄 GomGom AI 서버 업데이트 스크립트"
echo "=================================="

# 프로젝트 디렉토리로 이동
cd /home/ubuntu/gom

# 현재 상태 백업
echo "📦 현재 상태 백업 중..."
cp -r . ../gom_backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo "백업 디렉토리 생성 실패 (무시 가능)"

# Git에서 최신 코드 가져오기
echo "📥 Git에서 최신 코드 가져오기..."
git fetch origin
git reset --hard origin/main

# 가상환경 활성화
echo "🐍 가상환경 활성화..."
source venv/bin/activate

# 의존성 업데이트
echo "📦 Python 의존성 업데이트..."
pip install -r requirements.txt

# 데이터베이스 마이그레이션 (필요한 경우)
echo "🗄️  데이터베이스 마이그레이션 확인..."
if [ -f "alembic.ini" ]; then
    alembic upgrade head
fi

# 프론트엔드 빌드 (Next.js가 있는 경우)
if [ -d "frontend" ]; then
    echo "🎨 프론트엔드 빌드 중..."
    cd frontend
    npm install
    npm run build
    cd ..
fi

# PM2 프로세스 재시작
echo "🔄 PM2 프로세스 재시작..."
pm2 restart gomgom-ai

# 상태 확인
echo "📊 서버 상태 확인..."
pm2 status

echo ""
echo "✅ 서버 업데이트 완료!"
echo "📝 로그 확인: pm2 logs gomgom-ai"
echo "🔍 실시간 로그: pm2 logs gomgom-ai --lines 100" 