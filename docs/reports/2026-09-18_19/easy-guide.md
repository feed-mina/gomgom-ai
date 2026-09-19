# gomgom-ai — easy-guide 쉬운 업데이트 설명

한국시간 2026년 9월 18~19일 업데이트 보고서. 활동 집계 마감은 9월 19일 21:24:15입니다.

입력한 음식·기분과 취향으로 식당을 추천하는 프로젝트입니다. 이번에는 기존 화면 외에 화면편집기가 사용할 JSON 요청 창구가 추가됐습니다.

| 항목 | 기준 |
|---|---|
| 보고서 범위 | 이번 기간의 변경과 관련 기능. 전체 시스템 설명은 아래 기존 상세 문서로 연결합니다. |
| 확인 브랜치 | main |
| 소스 기준 | `382249fef5e1` |
| 검증 범위 | 분리 검사에서 types=["active"]는 정상 응답, types=[{}]는 TypeError: unhashable type: dict를 재현했습니다. |
| 보고서 세트 | [쉬운 설명](easy-guide.md) · [수정·검증 지시](fix-guide.md) · [코드 인수인계](screen-code-handover.md) |

## 이번에 달라진 것

- 9월 18일 인수인계 PDF를 추가했습니다.
- 9월 19일 PR #2로 추천·주변 식당 JSON API, manifest와 입력·출력 규칙을 추가했습니다.
- 화면편집기 저장소의 gomgom 호스트 플러그인이 이 창구를 호출하도록 별도로 추가됐습니다.

## 1. 용어와 원리

| 용어 | 쉬운 뜻과 이번 작업에서의 역할 |
|---|---|
| JSON (JavaScript Object Notation, 구조화된 데이터 표기) | 화면 대신 값 묶음을 전달해 다른 화면에서도 같은 결과를 표시하도록 합니다. |
| CORS (Cross-Origin Resource Sharing, 다른 출처의 요청 허용 규칙) | 허용한 웹사이트가 응답을 읽을 수 있도록 브라우저에 알려줍니다. |
| Cache (캐시) | 같은 좌표의 식당 목록을 잠시 보관해 다시 씁니다. 현재 목록 API는 5분 캐시를 사용합니다. |

## 2. 익숙한 상황에 빗대어 보기

식당 추천 직원이 말로만 답하던 것을 주문서에도 적어 주게 된 작업입니다. 편집기는 주문서를 읽어 자기 화면에 보여줍니다. 주문서의 취향 칸에는 정해진 문자열을 넣어야 하는데, 다른 형태가 들어왔을 때의 검사가 빠져 있습니다.

이 비유는 역할을 이해하기 위한 설명입니다. 실제 저장·승인·실행 조건은 코드 인수인계 보고서를 기준으로 확인합니다.

## 3. 서로 어떻게 연결되는가

Studio 입력은 호스트 플러그인을 거쳐 recommend_api로 갑니다. 응답의 store·description·category가 결과 카드에 표시됩니다. 주변 목록은 좌표별 캐시를 사용하며 최대 20개를 반환합니다.

| 산출물 | 읽고 판단할 일 |
|---|---|
| easy-guide | 무엇이 달라졌고 어디까지 가능한지 이해 |
| fix-guide | types 배열 원소가 객체일 때 입력 오류 대신 TypeError 발생 |
| screen-code-handover | 화면·함수·입력·출력·저장 위치를 따라 유지보수 |

## 4. 직접 확인하는 순서

1. API 계약과 manifest에서 두 요청 경로를 확인합니다. 성공 기준: 추천 POST와 목록 GET을 구분합니다.
2. fix-guide의 types 정상 배열과 객체 원소 배열을 비교합니다. 성공 기준: 입력 오류를 서버 예외로 방치하는 위치를 찾습니다.
3. 전체 연결 확인은 로컬 모의 추천으로 시작합니다. 외부 추천 실패는 API 오류와 화면 안내를 함께 기록합니다.

## 확인한 활동

| 한국시간 | 커밋 | 기록된 작업 | 구분 |
|---|---|---|---|
| 09/19 15:49 | [382249f](https://github.com/feed-mina/gomgom-ai/commit/382249fef5e1ef15d015f47ce4426e5840fbff94) | Merge pull request #2 from feed-mina/sdui/main-manifest | 병합 기록 |
| 09/19 13:12 | [573f327](https://github.com/feed-mina/gomgom-ai/commit/573f327abbda6b8baf2dd9755da1ba210fb000b4) | feat(sdui): 메인 화면 SDUI manifest와 추천 JSON 창구 추가 | 변경 기록 |
| 09/18 19:04 | [74892ac](https://github.com/feed-mina/gomgom-ai/commit/74892ac2e75bc89abe4390a41069c4de31937cc8) | Merge pull request #1 from feed-mina/copilot/create-hand-off-documentation | 병합 기록 |
| 09/18 19:02 | [8a0c9e5](https://github.com/feed-mina/gomgom-ai/commit/8a0c9e577e3101b2ab66cb08df728f9ef2a9829c) | Add screen-to-code handover PDF | 변경 기록 |

커밋은 파일 변경 기록이고 병합은 작업 브랜치를 합친 기록입니다. 둘을 별개의 기능 수로 세지 않습니다. 에이전트가 작성한 커밋도 사용자 저장소의 작업으로 포함했습니다.

## 기존 상세 자료

- [API 계약](https://github.com/feed-mina/gomgom-ai/blob/382249fef5e1ef15d015f47ce4426e5840fbff94/sdui/gomgom-ai/api-contract.md)
- [기존 인수인계 PDF](https://github.com/feed-mina/gomgom-ai/blob/382249fef5e1ef15d015f47ce4426e5840fbff94/GOMGOM-AI_%ED%99%94%EB%A9%B4-%EC%BD%94%EB%93%9C-%EC%9D%B8%EC%88%98%EC%9D%B8%EA%B3%84.pdf)
- [Studio 연결 코드](https://github.com/feed-mina/sdui-template-kit-productization/blob/4ffa0608a65718032a986c53542c3e6a72b13ca4/studio/sdui-gomgom.js)
