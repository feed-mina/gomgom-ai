# gomgom-ai — fix-guide 수정·검증 지시

한국시간 2026년 9월 18~19일 업데이트 보고서. 활동 집계 마감은 9월 19일 21:24:15입니다.

입력한 음식·기분과 취향으로 식당을 추천하는 프로젝트입니다. 이번에는 기존 화면 외에 화면편집기가 사용할 JSON 요청 창구가 추가됐습니다.

| 항목 | 기준 |
|---|---|
| 보고서 범위 | 이번 기간의 변경과 관련 기능. 전체 시스템 설명은 아래 기존 상세 문서로 연결합니다. |
| 확인 브랜치 | main |
| 소스 기준 | `382249fef5e1` |
| 검증 범위 | 분리 검사에서 types=["active"]는 정상 응답, types=[{}]는 TypeError: unhashable type: dict를 재현했습니다. |
| 보고서 세트 | [쉬운 설명](easy-guide.md) · [수정·검증 지시](fix-guide.md) · [코드 인수인계](screen-code-handover.md) |

## 0. 식별과 상태

**types 배열 원소가 객체일 때 입력 오류 대신 TypeError 발생**

[2026-09-18~19 KST / gomgom_ai/views.py (28,106바이트, 755줄, 파일 지문 be17d23e9b68) / main]

상태: **실제 함수의 외부 의존성 분리 검사로 재현**. 이번 변경은 보고서 작성이며, 아래 애플리케이션 수정이나 운영 작업은 실행하지 않았습니다.

## 1. 현상

| 기대 | 확인한 실제 상태 |
|---|---|
| 잘못된 취향 입력은 VALIDATION_ERROR 응답이어야 합니다. | {"text":"밥","types":[{}]}를 넣으면 set 멤버십 검사에서 TypeError가 발생합니다. 정상 문자열 배열은 모의 추천 결과를 반환합니다. |

## 2. 원인과 근거

recommend_api의 `t in VALID_TASTE_TYPES` 앞에 원소별 문자열 검사가 없습니다. 이 줄은 run_recommend를 감싼 try 밖입니다.

[기준 소스 열기](https://github.com/feed-mina/gomgom-ai/blob/382249fef5e1ef15d015f47ce4426e5840fbff94/gomgom_ai/views.py)

## 3. 수정 위치

- gomgom_ai/views.py — recommend_api의 types 검사·필터
- sdui/gomgom-ai/contracts/gomgom-recommend-run.input.schema.json — 입력 계약 대조

## 4. 수정 또는 확인 방법

1. 배열 여부와 함께 모든 원소가 문자열인지 검사합니다.
2. 자료형이 잘못되면 기존 _error로 VALIDATION_ERROR를 반환합니다.
3. 기존 최대 6개·허용 태그 필터·정상 추천 동작을 보존합니다.

변경 전 코드:

```python
if not isinstance(types, list):
    return _error('VALIDATION_ERROR', 'types 는 배열이어야 합니다.', request)
types = [t for t in types[:6] if t in VALID_TASTE_TYPES]
```

제안하는 변경 예시:

```python
if not isinstance(types, list) or any(not isinstance(t, str) for t in types):
    return _error('VALIDATION_ERROR', 'types 는 문자열 배열이어야 합니다.', request)
types = [t for t in types[:6] if t in VALID_TASTE_TYPES]
```

예시는 제안이며 저장소 코드에 반영된 내용이 아닙니다.

## 5. 완료 기준

- [ ] types=[{}]와 types=[[]]는 외부 추천 호출 없이 입력 오류를 반환합니다.
- [ ] types=["active"]는 기존 정상 응답 구조를 유지합니다.
- [ ] 알 수 없는 문자열 태그의 기존 필터 정책과 최대 개수 제한이 유지됩니다.

## 6. 검증 방법과 제출할 근거

먼저 분리 함수 검사로 정상·오류 입력을 확인하고, 이어 Django 요청 테스트에서 HTTP 상태와 {ok,data,errors} 봉투를 검사합니다. 외부 모델은 모의 객체로 대체합니다.

실행 결과·캡처·응답 본문 중 완료 기준에 해당하는 근거를 남깁니다. 미실행 항목은 완료로 표시하지 않습니다.
