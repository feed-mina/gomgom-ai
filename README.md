# Click Your Taste! (Gomgom-AI)

> **"OpenAI GPT와 지리 기반 서비스(Kakao 지도)를 비동기와 Redis 캐시로 최적화한 커스텀 식당 추천 AI"**

![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-Cache-DC382D?logo=redis&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT_3.5-412991?logo=openai&logoColor=white)

## 📌 1. 프로젝트 개요

사용자의 기분, 날씨, 자유 입력 구문을 바탕으로 **가장 어울리는 음식 카테고리를 추론하고**, 사용자의 **현재 위치(GPS) 기준 근처 음식점을 즉각 추천**해 주는 웹서비스입니다.
외부 의존성이 높은 AI 프로토콜 환경에서 **응답 시간(Latency) 최소화와 비동기 처리에 집중**하여 백엔드 최적화를 연습한 실무형 포트폴리오 프로젝트입니다.

* **🚀 서버 상태:** AWS 인프라 비용 소진으로 현재 호스팅이 종료되었습니다. 하단의 **로컬 실행 가이드**를 참조해 주세요.

---

## 🏗 2. 아키텍처 및 핵심 플로우 (Architecture Flow)

### ⚡ 외부 API 비동기 및 캐시 처리 엔진
사용자의 단순 입력을 OpenAI가 분석하고, 이를 외부 식당(요기요) 데이터와 연결하는 파이프라인에서 생길 수 있는 Gunicorn 시스템 병목 현상(I/O Block)을 해결했습니다.

```text
[ Client (UI) ] ── (자유 감정 텍스트 입력) ──▶ [ Django Server (Async httpx) ]
                                              │
      [ 1. 캐시 히트? ] ◀───(Cache Hit 판단)─── [ Redis (자주 찾는 쿼리/태그 캐싱) ]
                                              │
                                              ▼ (Cache Miss: 외부 비동기 호출)
                                         [ OpenAI GPT API (자연어 카테고리화) ]
                                         [ Kakao Local API (좌표 → 주소 변환) ]
                                         [ 식당 API (음식점 위치 및 옵션 패치) ]
                                              │
[ 결과 화면 (식당 리스트 렌더링) ] ◀──(결과 조합 응답 및 Redis 데이터 갱신)───┘
```

---

## 🔥 3. 기술 의사결정 (Tech Reasoning)

### ① AI/서드파티 API 통신 지연을 잡기 위한 Httpx(비동기) 도입
* GPT API와 식당 데이터 API 등 무거운 요청이 동기적(Synchronous)으로 진행될 경우 전체 스레드가 멈추어 사용자 대기 시간(UX)이 파괴됨을 인지했습니다.
* 파이썬의 `httpx`를 이용해 Django 내부의 통신 프로토콜을 백그라운드 **비동기 통신(Asynchronous Iteration)**으로 전환하여 시스템 응답 탄력성을 극대화했습니다. 

### ② 반복 연산 해소: Redis 인메모리 캐싱 아키텍처
* 1회성 테스트 결과, 동일한 기분("매운 음식 먹고 싶어", "우울해")이나 동일한 주소(강남역 근처)에 대해 동일한 추천 API를 찌르는 것이 낭비라고 타겟팅했습니다.
* 매핑된 감정 카테고리나 가게 리스트를 서버 내부의 **Redis를 통해 캐싱 정책**을 도입하여 런타임 성능을 대폭(Cash Miss 대비 약 40% 이상 속도 감소율 확보) 시켰습니다.

---

## 🛠 4. 기술 스택 (Tech Stack)

### Backend Engine
* **Framework:** Python, Django 5.2
* **Asynchronous Call:** httpx
* **Caching:** Redis, Django Cache Framework
* **3rd Party AI/API:** OpenAI API (GPT-3.5), Kakao Map/Local API, 요기요 외부 비공식 API 

### Frontend & Infra
* **Templating:** HTML/CSS, Vanilla JS, Jinja2 (Django Template)
* **Server Deployment:** Ubuntu EC2, Nginx, Gunicorn (ASGI 지원 셋팅)

---

## 📝 5. 주요 기능 명세 (Features)

* **감성 추론 알고리즘:** "오늘 헤어졌어.. 위로가 필요해" → GPT가 "맵고 스트레스 풀리는 음식(불닭, 마라탕 등)"으로 자동 분류
* **지리적 정합성:** HTML GeoLocation API를 통해 x, y 좌표를 뽑아내고, 이를 Kakao Local API로 도로명 규격으로 정규화(Normalize)
* **사용자 심리 테스트 플로우:** 6~10개의 단순 문항 기반 심리학적 추천 MBTI/루틴 파이프라인

## 📝 5. 핵심 기획 및 문서화 (Documentation)

단순 개발을 넘어 시스템 플로우 모델링 및 API 명세화를 철저히 기획했습니다. 본 저장소 루트에 포함된 기획 문서를 확인하실 수 있습니다.
* 📄 **[GOMGOM-AI 전체 기능별 시퀀스 문서.pdf](./GOMGOM-AI%20전체%20기능별%20시퀀스%20문서%20.pdf)**: AI 시스템 연동 및 사용자 데이터 간의 Sequence 플로우 차트.
* 📄 **[Gomgom Ai_프로젝트_문서화.pdf](./Gomgom%20Ai_프로젝트_문서화.pdf)**: 시스템 요구사항 및 기획안 상세.

---

## 🚀 6. 로컬 실행 방법 (Getting Started)

### 환경 설정 및 서버 구동
```bash
git clone https://github.com/feed-mina/gomgom-ai.git
cd gomgom_ai

# 가상환경 구축 
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)

# 의존성 설치
pip install -r requirements.txt

# DB 마이그레이션 & 실행
python manage.py migrate
python manage.py runserver
```

### 🔑 `.env` 키 셋팅 필요 (루트 디렉토리)
로컬에서 테스트하려면 발급받은 외부 서비스 인증키를 설정해야 합니다.
```env
OPENAI_API_KEY=sk-xxxx....
KAKAO_REST_API=xxxx....
```

---
*Developed by Min Yerin (2년 차 풀스택/백엔드 개발자)* 
*Contacts: dbdlstltm94@gmail.com*
