# 🍚 CLICK YOUR TASTE! - 밥꾹

"오늘은 뭘 먹을까?" 고민하는 당신을 위한 귀여운 메뉴 추천 서비스입니다.  
토끼 셰프와 함께, 다양한 상황과 입맛에 맞는 메뉴를 추천받아보세요!

---

## 📌 프로젝트 소개

- **프로젝트명**: 밥꾹 (CLICK YOUR TASTE!)
- **타겟 사용자**: 메뉴 선택에 어려움을 느끼는 사람들
- **기술 스택**:
  - HTML / CSS / JavaScript (Vanilla)
  - Django + MySQL (결과 저장 기능)
- **디자인 포인트**:
  - 아기자기한 일러스트와 파스텔톤 UI
  - 단계별 선택 방식 UX
  - 타이핑 효과와 애니메이션 효과

---

## 🗂️ 프로젝트 구조

```bash
📁 esgproject-Merge_frontend/
│
├── html/
│   ├── main.html               # 첫 화면 (타이핑 + 버튼)
│   ├── situation.html          # 상황 선택
│   ├── situation2.html         # 음식 종류 선택
│   ├── situation3.html         # 추가 옵션 선택 (ex. 국물)
│   ├── situation4.html         # 마지막 선택
│   ├── result.html             # 랜덤 추천 결과
│   ├── start.html              # 입맛 테스트 시작
│   ├── question.html           # 테스트 질문 페이지
│   └── test_result.html        # 테스트 결과 페이지
│
├── css/
│   ├── main.css                # 전체 스타일 정의
│
├── javascript/
│   ├── main.js                 # 타이핑 효과 및 버튼 처리
│
└── 📦 Backend (Django, 추후 추가 예정)
```

---

## ✅ 주요 기능

| 기능 | 설명 |
|------|------|
| 🎲 랜덤 추천 | 상황 → 음식 종류 → 조건 → 메뉴 추천 |
| 🧠 입맛 테스트 | 여러 질문을 통해 음식 타입 추천 |
| 🐰 귀여운 UI | 토끼 셰프 일러스트와 파스텔 톤 디자인 |
| 📝 결과 저장 | 테스트 결과를 DB에 저장 (Django 백엔드 연동) |

---

## 🛠️ 향후 구현 예정 기능

- [x] 테스트 결과를 DB에 저장하기
- [ ] Vue.js 또는 Django 템플릿으로 전환
- [ ] 관리자가 추천 데이터를 조회할 수 있는 관리자 페이지 만들기
- [ ] 결과 공유 기능 (카카오톡/URL 복사 등)

---

## 🧪 테스트 결과 저장 API (Django)

**요청 방식**: `POST`  
**URL**: `/api/save_result`

```json
{
  "answer1": "answerA",
  "answer2": "answerB",
  "answer3": "answerC",
  "answer4": "answerD",
  "answer5": "answerE",
  "answer6": "answerF",
  "result_type": "homeFood",
  "recommended_menu": "비빔막국수(for vegan)"
}
```

```js
// JS에서 보내는 예시 코드
fetch("http://localhost:8000/api/save_result", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    answer1: "answerA",
    answer2: "answerB",
    answer3: "answerC",
    answer4: "answerD",
    answer5: "answerE",
    answer6: "answerF",
    result_type: "homeFood",
    recommended_menu: "비빔막국수(for vegan)"
  })
});
```

---

## 💾 DB 테이블 생성 SQL (MySQL)

```sql
CREATE TABLE test_results (
  id INT AUTO_INCREMENT PRIMARY KEY,
  answer1 VARCHAR(50),
  answer2 VARCHAR(50),
  answer3 VARCHAR(50),
  answer4 VARCHAR(50),
  answer5 VARCHAR(50),
  answer6 VARCHAR(50),
  result_type VARCHAR(50),
  recommended_menu TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🐍 Django 백엔드 코드 (views.py)

```python
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import TestResult

@csrf_exempt
def save_result(request):
    if request.method == "POST":
        data = json.loads(request.body)
        TestResult.objects.create(
            answer1=data["answer1"],
            answer2=data["answer2"],
            answer3=data["answer3"],
            answer4=data["answer4"],
            answer5=data["answer5"],
            answer6=data["answer6"],
            result_type=data["result_type"],
            recommended_menu=data["recommended_menu"]
        )
        return JsonResponse({"message": "saved"})
```

---

## 🔗 URL 설정 (urls.py)

```python
from django.urls import path
from . import views

urlpatterns = [
    path('api/save_result', views.save_result),
]
```

---

## 📦 Django 모델 정의 (models.py)

```python
from django.db import models

class TestResult(models.Model):
    answer1 = models.CharField(max_length=50)
    answer2 = models.CharField(max_length=50)
    answer3 = models.CharField(max_length=50)
    answer4 = models.CharField(max_length=50)
    answer5 = models.CharField(max_length=50)
    answer6 = models.CharField(max_length=50)
    result_type = models.CharField(max_length=50)
    recommended_menu = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 🧸 Special Thanks

이 프로젝트는 귀여운 UI/UX로 사용자에게 즐거운 식사 결정을 도와주고자 만들어졌습니다.  
아이디어에서 배포까지, 모든 과정을 스스로 기획하고 개발한 미니 프로젝트입니다.

> 만든 사람: **햄** (MIN YERIN)

