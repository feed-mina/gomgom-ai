#!/bin/bash

echo "🔄 GomGom AI 서버 업데이트 스크립트"
echo "=================================="

# 현재 디렉토리 확인
CURRENT_DIR=$(pwd)
echo "📍 현재 디렉토리: $CURRENT_DIR"

# 백엔드 업데이트
echo "🔧 백엔드 업데이트 시작..."
cd /home/ubuntu/backend

# 현재 상태 백업
echo "📦 백엔드 상태 백업 중..."
cp -r . ../backend_backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo "백업 디렉토리 생성 실패 (무시 가능)"

# Git에서 최신 코드 가져오기
echo "📥 Git에서 최신 코드 가져오기..."
git fetch origin
git reset --hard origin/main

# 가상환경 활성화 (Python 3.11 사용)
echo "🐍 가상환경 활성화..."
source venv-py311/bin/activate

# Python 버전 확인
echo "🐍 Python 버전 확인..."
python --version

# 의존성 업데이트
echo "📦 Python 의존성 업데이트..."
pip install --upgrade pip
pip install -r requirements.txt

# 데이터베이스 마이그레이션 (필요한 경우)
echo "🗄️  데이터베이스 마이그레이션 확인..."
if [ -f "alembic.ini" ]; then
    alembic upgrade head
fi

# 프론트엔드 업데이트
echo "🎨 프론트엔드 업데이트 시작..."
cd /home/ubuntu/frontend

# 현재 상태 백업
echo "📦 프론트엔드 상태 백업 중..."
cp -r . ../frontend_backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo "백업 디렉토리 생성 실패 (무시 가능)"

# Git에서 최신 코드 가져오기
echo "📥 Git에서 최신 코드 가져오기..."
git fetch origin
git reset --hard origin/main

# Node.js 의존성 설치 및 빌드
echo "📦 Node.js 의존성 설치..."
npm install

echo "🔨 프론트엔드 빌드 중..."
npm run build

# PM2 프로세스 재시작
echo "🔄 PM2 프로세스 재시작..."
cd /home/ubuntu/backend
pm2 restart gomgom-ai

# 상태 확인
echo "📊 서버 상태 확인..."
pm2 status

echo ""
echo "✅ 서버 업데이트 완료!"
echo "📝 로그 확인: pm2 logs gomgom-ai"
echo "🔍 실시간 로그: pm2 logs gomgom-ai --lines 100" 