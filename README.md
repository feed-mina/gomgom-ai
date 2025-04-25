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

 1단계: 어떤 조건을 사용자가 입력할 수 있을지 정하기
 2단계: 그 조건들을 문장(프롬프트)으로 어떻게 묶을지 설계하기
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

## 🤖 LLM 기반 추천 기능 추가

- 사용자가 입력한 성향 + 예산 정보를 기반으로
- OpenAI GPT API를 통해 맞춤형 추천 문장을 생성
- 추천된 메뉴와 함께 시각화하여 보여주는 기능 추가

### 📌 추천 API

**URL**: `/api/recommend_llm`  
**요청 방식**: `POST`

```json
{
  "budget": 12000,
  "result_type": "homeFood"
}{
  "recommended_menu": "청국장",
  "reason": "집밥 스타일을 선호하고 예산에 적합한 메뉴입니다."
}

```

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
 요기요 클론 API 기반 메뉴 추천 시스템 개발 계획

1. 목표
- 요기요 비공식 API를 Django에서 호출
- 메뉴/리뷰 데이터를 바탕으로 추천 후보군 생성
- LLM(OpenAI 등)에게 프롬프트를 전달해 자연어 메뉴 추천
- 추천 결과를 화면에 표시 + Chart.js로 시각화

2. 요기요 API 사용 흐름 (Postman 기준)
① 고객 세션 생성
② Access Token 발급
③ 배달 가능 여부 확인
④ 사용자 정보 조회
⑤ 가게 목록 조회
⑥ 가게별 메뉴 조회
⑦ 메뉴에 대한 리뷰 조회

3. Django 내 처리 흐름
- 사용자가 예산, 성향, 스타일 입력 (ex. 12000원, homeFood, 혼밥 등)
- Django에서 요기요 API를 호출해 메뉴/리뷰 데이터 수집
- 예산 범위 내 + 필터 조건으로 메뉴 리스트 필터링
- 필터링된 메뉴들을 기반으로 LLM에 질문 프롬프트 생성
- LLM이 추천 메뉴 1개 + 이유를 반환
- Django가 결과를 응답 + 시각화해서 보여줌

4. LLM 프롬프트 예시
"예산 12000원이고 혼밥 가능한 집밥 스타일을 찾고 있어.
아래 후보 중 추천 메뉴를 알려줘:
- 청국장 (8000원)
- 제육볶음 (9500원)
- 순두부찌개 (11000원)
추천 메뉴와 추천 이유를 알려줘."

5. 구현할 Django 기능
- [ ] `/api/recommend_llm` API 생성 (POST)
- [ ] 사용자가 입력한 조건 파라미터 받기
- [ ] 요기요 API에서 메뉴/리뷰 정보 요청
- [ ] 예산 및 조건 기반 필터링
- [ ] 추천 프롬프트 자동 생성
- [ ] OpenAI API 호출 후 응답 저장
- [ ] 추천 결과 반환 (메뉴 이름 + 이유 + 기타 정보)

6. 화면 구성
- 사용자가 조건 입력 (예산, 혼밥 여부, 스타일)
- 추천된 메뉴와 이유를 자연어로 출력
- 추천 후보 메뉴 가격, 평점 등은 Chart.js로 시각화

7. 기술 스택
- Django (REST API)
- requests (요기요 API 호출용)
- OpenAI (LLM 추천)
- Chart.js (추천 결과 시각화)
- Postman (API 테스트)
- EC2 배포 예정 (도메인: mindevprofile.kr)

 다음 단계
→ 요기요 API Django 코드부터 구현
→ 또는 LLM 프롬프트 자동 생성 로직부터 구현

→ 원하는 방향 선택해서 진행 가능!

---
- [ ] `/api/recommend_llm` API 새로 만들기
- [ ] `openai_utils.py`로 프롬프트 정리
- [ ] Chart.js 예제 화면 추가
---

## 👩‍💻 만든 사람

- 개발자: [햄 (Min Yerin)](https://github.com/feed-mina)
- GitHub: https://github.com/feed-mina
  [main.html]
  └── (입맛 테스트 버튼 클릭)
  → /start?text=...&lat=...&lng=...
  → [start_view] start.html 화면
  (여기서 "입맛 테스트 시작" 버튼 누르면)
  → /test
  → [test_view] test.html (문제 출제)
  (모든 문제 답변하면)
  → /test_result?type1=...&type2=...&lat=...&lng=...
  → [test_result_view] test_result.html (최종 결과)
  [main.html]
  └→ /start (text, lat, lng)
  └→ [start.html] (테스트 시작 버튼)
  └→ /test (lat, lng)
  └→ [test.html] (심리테스트 6문항)
  └→ /test_result (type1~6 + lat + lng)
  └→ [test_result.html] (최종 결과)





