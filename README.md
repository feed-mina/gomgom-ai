# gomgom-ai
곰곰이 생각해서  AI 메뉴 추천 웹사이트

# 🍱 AI 메뉴 추천 웹서비스

예산에 맞는 메뉴를 AI가 추천하고, 리뷰와 평점을 시각화해주는 웹 프로젝트입니다.  
요기요 데이터를 기반으로, OpenAI LLM API를 통해 사용자 맞춤 메뉴를 제안하고  
Chart.js로 직관적인 시각화를 제공합니다.

---
## 🧠 추천 시스템 작동 원리

1. 사용자가 다음 항목을 입력
   - 예산 (ex. 12,000원)
   - 선호 스타일 (ex. 혼밥, 국물 있는 음식)
   - 성향 태그 (ex. homeFood, indecisive 등)

2. Django API(`/api/recommend`)에서 해당 조건으로 메뉴 후보를 필터링

3. 필터링된 데이터를 기반으로 아래와 같은 형태의 LLM 프롬프트 생성:
"예산 12,000원으로 먹을 수 있는 혼밥 스타일의 국물 있는 한식을 추천해줘. 나는 homeFood 스타일을 좋아하고 우유부단한 편이야. 메뉴 이름과 이유를 알려줘."

4. LangChain(OpenAI)을 통해 자연어 추천 문장을 생성

5. 추천된 메뉴 및 이유를 사용자에게 반환 + Chart.js로 시각화

✅ 1단계: 어떤 조건을 사용자가 입력할 수 있을지 정하기
✅ 2단계: 그 조건들을 문장(프롬프트)으로 어떻게 묶을지 설계하기
➡️ 3단계: Django에서 이걸 API로 만들기 (/api/recommend)
➡️ 4단계: 그 안에서 LLM 호출 + 결과 응답
➡️ 5단계: 결과를 화면에 표시 + 시각화

## 🧠 시스템 구성도

- 사용자
  ↓
- **mindevprofile.kr (EC2 서버)**
  - Django: 웹페이지 + API
    - Chart.js: 예산 기반 시각화
    - `/recommend`: 메뉴 추천 API
  - LLM API (OpenAI): 추천 결과 생성
  - Yogiyo Clone: 메뉴/리뷰/가격 데이터 제공

---

## 🧩 개발 순서

1. **아이디어 구체화**
   - 만들고자 하는 기능 정리
   - 사용자 흐름 상상
   - 사용 기술(Django, OpenAI, Chart.js 등) 기본 개념 익히기

2. **기본 화면 설계**
   - 사용자 입력 화면 스케치 (예산 입력, 추천 결과, 그래프 등)

3. **Django 프로젝트 생성**
   - Django 설치 및 프로젝트 생성
   - 앱 생성 및 URL 설정

4. **Chart.js로 시각화 구현**
   - Mock 데이터로 그래프 구현
   - 사용자 입력에 따른 동적 그래프 생성

5. **OpenAI API 연결**
   - API 키 등록
   - 사용자 입력을 기반으로 메뉴 추천 기능 구현

6. **Yogiyo Clone 데이터 활용**
   - 기존 프로젝트에서 메뉴/리뷰 데이터 추출
   - AI 추천에 활용

7. **EC2 서버에 배포**
   - Gunicorn + Nginx 설정
   - 도메인 연결 및 배포 테스트

---

## 🧭 사용자 흐름

1. 메인 페이지
   - 예산 입력 칸
   - 위치 선택 옵션
   - “추천 받기” 버튼

2. 추천 결과 페이지
   - 추천된 음식 리스트 출력
   - 각 음식의 가격, 리뷰, 평점 표시
   - Chart.js를 이용한 그래프 시각화

3. 전체 흐름 예시
   - 사용자가 “12000원 있어요” 입력
   - OpenAI API가 메뉴 추천 생성 (예: “리뷰 좋은 족발 추천할게요!”)
   - Django가 결과를 웹에 표시
   - Chart.js가 그래프로 시각화 (금액 비교, 평점 등)

---

## 🛠 기술 스택

- **Backend**: Django
- **Frontend**: HTML, JavaScript, Chart.js
- **AI API**: OpenAI GPT (LangChain 활용 가능)
- **데이터**: 요기요 비공식 API Clone 프로젝트
- **배포**: AWS EC2 (mindevprofile.kr)

---

## 👩‍💻 만든 사람

- 개발자: [햄 (Min Yerin)](https://github.com/feed-mina)
- GitHub: https://github.com/feed-mina




