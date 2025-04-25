# Click Your Taste! - 입맛 기반 음식 추천 웹 서비스

내 기분과 취향, 현재 위치에 맞는 딱 맞는 음식점 추천

---

## 프로젝트 소개

Click Your Taste는 사용자의 기분/입맛 테스트와 현재 위치 정보를 바탕으로,
요기요 API와 GPT를 활용해 가장 잘 어울리는 배달 음식점 추천 웹 서비스입니다.

- GPT가 감성에 맞는 음식 카테고리 분석
- 현재 위치 기반 추천 (Geolocation + Kakao 주소 API)
- Redis + 캐싱 적용
- 요기요 비공식 API로 실시간 음식점 데이터 사용

---

## 핵심 기능

| 기능 | 설명 |
|------|------|
| 입력 기반 추천 | 사용자의 자유 입력(예: 매운 음식, 피곤해)에 맞춰 GPT 추천 |
| 입맛 테스트 | 6문항 심리테스트 → 기분 태그 생성 → GPT 추천 |
| 위치 기반 추천 | 현재 위치 기반 도로명 주소 + 근처 음식점 추천 |
| 다시 추천받기 | 추천 결과에서 "다른 가게 보기", "다시 추천받기" 가능 |
| 캐싱 처리 | Redis, Django 캐시로 API 호출 최적화 |

---

## 사용 기술 스택

| 항목 | 기술 |
|------|------|
| 프론트엔드 | HTML/CSS, JavaScript, Jinja2 (Django Template) |
| 백엔드 | Django 5.2, Python |
| AI 연동 | OpenAI GPT-3.5 API |
| 위치 서비스 | Kakao 지도 API (좌표 → 도로명 주소 변환) |
| 배달 정보 | 요기요 비공식 API 사용 |
| 기타 | Redis, Nginx, EC2, Gunicorn, ASGI 지원, httpx (비동기) |

---

## 서비스 흐름도

main.html
├─ 입력 추천 → /recommend_result/
└─ 입맛 테스트 → /start → /test → /test_result

---

## 주요 화면

| 메인화면                      | 테스트 결과                                          |
|---------------------------|-------------------------------------------------|
| ![main](https://mindevprofile.kr) | ![result](https://mindevprofile.kr/test_result) |

---

## 환경변수 (.env)

OPENAI_API_KEY=sk-xxxx
KAKAO_REST_API=xxxxxxxxxxxxxxxx

---

## 실행 방법

1. 가상환경 실행 및 패키지 설치
```bash
python -m venv venv
source venv/bin/activate  # 윈도우: venv\Scripts\activate
pip install -r requirements.txt
```

2. Django 서버 실행
```bash
python manage.py runserver
```

3. .env에 API 키 설정 필요

---

## 개발자

| 이름 | 역할 |
|------|------|
| 민예린  | 풀스택 개발, 기획, 디자인, 배포 |

포트폴리오: https://justsaying.co.kr  
GitHub: https://github.com/feed-mina

---

## 추후 개선사항

- 음식점 상세 메뉴까지 분석
- 이미지 기반 추천 (음식 사진 → 감정 매칭)
- GPT-4 전환 및 응답 퀄리티 향상

---

## 문의

궁금한 점은 언제든지 GitHub Issues 또는 이메일로 연락 주세요.  
이메일: dbdlstltm94@gmail.com