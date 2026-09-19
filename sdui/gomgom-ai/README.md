# SDUI 템플릿 패키지 — gomgom-ai

곰곰 화면을 [SDUI Template Kit](https://github.com/feed-mina/sdui-template-kit-productization)의
Studio 편집기에서 열고 게시하기 위한 화면 정의 패키지입니다.

| 파일 | 역할 |
|---|---|
| `template.manifest.json` | 화면 정의(`feedmina.sdui.template.v1`). Studio 가져오기의 입력 |
| `contracts/*.schema.json` | 플러그인 action·hydrator 의 입출력 JSON Schema |
| `api-contract.md` | 백엔드 창구 요약 |

## 대응하는 백엔드 창구

| manifest 선언 | Django 경로 | 뷰 |
|---|---|---|
| `gomgom.recommend.run` (action) | `POST /api/v1/gomgom/recommend` | `views.recommend_api` |
| `gomgom.restaurants.nearby` (hydrator) | `GET /api/v1/gomgom/restaurants` | `views.restaurants_api` |

추천 계산은 기존 `views.run_recommend()` 를 그대로 쓰며, 화면용 HTML 경로
(`/test_result/`, `/recommend_result/`)는 변경 없이 유지됩니다.

## 검증

```bash
# sdui-template-kit-productization 저장소에서
node ./bin/sdui-kit.js validate <이 폴더>/template.manifest.json
node ./bin/sdui-kit.js import <이 폴더> --target cloudflare-worker-static --dry-run
```

`Manifest OK` 와 `pluginCompatibility.status: "ready"` 가 나와야 합니다.

## 플러그인 스크립트

버튼 클릭을 실제 창구 호출로 바꾸는 스크립트(`sdui-gomgom.js`)는 게시 호스트가
서빙해야 하므로 키트 저장소의 `studio/` 에 있습니다(`entryMode: "host"`).
