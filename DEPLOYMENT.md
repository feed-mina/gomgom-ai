# GomGom AI EC2 배포 가이드

## 프로젝트 구조
```
/home/ubuntu/
├── backend/          # FastAPI 백엔드
├── frontend/         # Next.js 프론트엔드
└── gom/             # 기존 통합 프로젝트 (참고용)
```

## 초기 설정 (최초 1회)

### 1. EC2 서버 접속
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 2. 프로젝트 클론
```bash
cd /home/ubuntu

# 백엔드 클론
git clone https://github.com/your-username/gomgomai_.git backend
cd backend

# 프론트엔드 클론 (별도 저장소인 경우)
cd /home/ubuntu
git clone https://github.com/your-username/gomgomai-frontend.git frontend
```

### 3. 백엔드 설정
```bash
cd /home/ubuntu/backend

# Python 3.11 설치 확인
python3.11 --version

# 가상환경 생성 (Python 3.11 사용)
python3.11 -m venv venv-py311

# 가상환경 활성화
source venv-py311/bin/activate

# pip 업그레이드
pip install --upgrade pip

# 의존성 설치
pip install -r requirements.txt
```

### 4. 환경 변수 설정
```bash
cd /home/ubuntu/backend
cp env.example .env
# .env 파일을 편집하여 실제 값으로 변경
nano .env
```

### 5. 데이터베이스 설정
```bash
cd /home/ubuntu/backend
# PostgreSQL 연결 확인
# Redis 연결 확인
# 필요한 경우 마이그레이션 실행
alembic upgrade head
```

### 6. 프론트엔드 설정
```bash
cd /home/ubuntu/frontend

# Node.js 의존성 설치
npm install

# 환경 변수 설정 (필요한 경우)
cp .env.example .env.production
nano .env.production

# 빌드
npm run build
```

### 7. PM2 설치 및 서버 시작
```bash
# PM2 전역 설치
npm install -g pm2

# 실행 권한 부여
cd /home/ubuntu/backend
chmod +x start_server.sh

# 서버 시작
./start_server.sh
```

## 업데이트 방법

### 방법 1: 자동 업데이트 스크립트 사용 (권장)
```bash
# EC2 서버에서 실행
cd /home/ubuntu/backend
chmod +x update_server.sh
./update_server.sh
```

### 방법 2: 수동 업데이트
```bash
# 1. 백엔드 업데이트
cd /home/ubuntu/backend
git fetch origin
git reset --hard origin/main
source venv-py311/bin/activate
pip install -r requirements.txt
alembic upgrade head

# 2. 프론트엔드 업데이트
cd /home/ubuntu/frontend
git fetch origin
git reset --hard origin/main
npm install
npm run build

# 3. PM2 재시작
cd /home/ubuntu/backend
pm2 restart gomgom-ai
```

## 유용한 명령어

### PM2 관리
```bash
# 서버 상태 확인
pm2 status

# 로그 확인
pm2 logs gomgom-ai

# 실시간 로그 (최근 100줄)
pm2 logs gomgom-ai --lines 100

# 서버 재시작
pm2 restart gomgom-ai

# 서버 중지
pm2 stop gomgom-ai

# 서버 시작
pm2 start gomgom-ai
```

### 데이터베이스 관리
```bash
cd /home/ubuntu/backend
# 마이그레이션 생성
alembic revision --autogenerate -m "설명"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 상태 확인
alembic current
```

### 로그 확인
```bash
# PM2 로그
pm2 logs gomgom-ai

# 시스템 로그
sudo journalctl -u pm2-ubuntu

# Nginx 로그 (사용하는 경우)
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 문제 해결

### 서버가 시작되지 않는 경우
1. 로그 확인: `pm2 logs gomgom-ai`
2. 환경 변수 확인: `/home/ubuntu/backend/.env` 파일
3. 데이터베이스 연결 확인
4. 포트 충돌 확인: `sudo netstat -tlnp | grep 8000`

### 의존성 문제
```bash
# 백엔드 가상환경 재생성
cd /home/ubuntu/backend
rm -rf venv-py311
python3.11 -m venv venv-py311
source venv-py311/bin/activate
pip install -r requirements.txt
```

### 권한 문제
```bash
# 파일 권한 수정
chmod +x *.sh
chmod 755 /home/ubuntu/backend
chmod 755 /home/ubuntu/frontend
``` 