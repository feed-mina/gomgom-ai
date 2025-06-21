# GomGom AI 배포 가이드

## Ubuntu 서버에서 PM2로 배포하기

### 1. 사전 요구사항
- Python 3.8+
- Node.js 및 PM2
- PostgreSQL
- Redis
- OpenAI API 키

### 2. 환경 설정

#### 2.1 환경 변수 설정
```bash
# .env 파일 생성 (프로젝트 루트에)
cp .env.example .env
# .env 파일을 편집하여 실제 값으로 변경
nano .env
```

필수 환경 변수:
- `OPENAI_API_KEY`: OpenAI API 키
- `POSTGRES_PASSWORD`: PostgreSQL 비밀번호
- 기타 데이터베이스 및 Redis 설정

#### 2.2 데이터베이스 설정
```bash
# PostgreSQL 서비스 시작
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 데이터베이스 생성
sudo -u postgres psql
CREATE DATABASE gomgomdb;
CREATE USER postgres WITH PASSWORD 'postgres1234';
GRANT ALL PRIVILEGES ON DATABASE gomgomdb TO postgres;
\q
```

#### 2.3 Redis 설정
```bash
# Redis 서비스 시작
sudo systemctl start redis
sudo systemctl enable redis
```

### 3. 애플리케이션 배포

#### 3.1 의존성 설치
```bash
# Python 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# Python 패키지 설치
pip install -r requirements.txt
```

#### 3.2 PM2 설치 및 설정
```bash
# PM2 전역 설치
npm install -g pm2

# 실행 권한 부여
chmod +x start_server.sh

# 애플리케이션 시작
./start_server.sh
```

### 4. PM2 명령어

```bash
# 상태 확인
pm2 status

# 로그 확인
pm2 logs gomgom-ai

# 애플리케이션 재시작
pm2 restart gomgom-ai

# 애플리케이션 중지
pm2 stop gomgom-ai

# 애플리케이션 삭제
pm2 delete gomgom-ai

# PM2 시작 시 자동 실행 설정
pm2 startup
pm2 save
```

### 5. 문제 해결

#### 5.1 일반적인 에러
- **SyntaxError: Invalid or unexpected token**: PM2가 Python 스크립트를 Node.js로 실행하려고 할 때 발생
  - 해결: `ecosystem.config.js`에서 `interpreter` 설정 확인
- **ModuleNotFoundError**: Python 패키지가 설치되지 않았을 때 발생
  - 해결: `pip install -r requirements.txt` 실행
- **ConnectionError**: 데이터베이스나 Redis 연결 실패
  - 해결: 서비스 상태 확인 및 환경 변수 설정 확인

#### 5.2 로그 확인
```bash
# 에러 로그 확인
pm2 logs gomgom-ai --err

# 전체 로그 확인
pm2 logs gomgom-ai --lines 100
```

### 6. 모니터링
```bash
# PM2 모니터링 대시보드
pm2 monit

# 시스템 리소스 사용량 확인
pm2 show gomgom-ai
```

### 7. 업데이트
```bash
# 코드 업데이트 후
git pull origin main
pip install -r requirements.txt
pm2 restart gomgom-ai
``` 