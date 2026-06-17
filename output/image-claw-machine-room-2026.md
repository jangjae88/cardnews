# Image Report: 뽑기방이 인기있는 이유

결론:
1. 이번 회차는 PNG/JPG 사진 소재 없이 HTML/CSS/SVG 및 PyMuPDF 라인워크만으로 충분하다.
2. 핵심 비주얼은 `무인 입구 -> 유리 진열장 -> 캡슐/집게 -> 결제 -> 반복 방문` 흐름으로 잡는다.
3. 특정 캐릭터/IP를 연상시키는 인형·굿즈는 모두 피하고, 추상 실루엣과 기하 도형으로 처리한다.

## 카드별 비주얼 제작 설명

- 카드 1 Hook: 어두운 유리 진열장 안에 캡슐 20~30개, 얇은 반사선, 집게 암을 배치한다.
- 카드 2 Experience: 작은 금액, 결과 확인, 소장품을 3개 라벨 패널로 분해한다.
- 카드 3 Domestic: 무인 입구, 카드 단말기, 매장 아이콘 반복으로 문턱이 낮아진 구조를 보여준다.
- 카드 4 Global: 캡슐 그리드와 블라인드박스 선반을 2열 비교로 배치한다.
- 카드 5 Guardrail: 공정성, 경품 기준, 민원 리스크를 게이트형 패널로 구성한다.
- 카드 6 Takeaway: Before/After와 체크리스트를 대시보드처럼 배치한다.

## 예비 생성 프롬프트

```text
A realistic but minimal vector-style glass claw machine display in warm tan and black, reflective glass lines, capsule shapes, payment terminal, no characters, no branded toys, clean editorial infographic style, high contrast, Instagram carousel background asset.
```

```text
Minimal commercial arcade unmanned capsule store interior, black glass cabinet, warm tan labels, thin white reflection lines, abstract geometric prizes only, no recognizable IP, no cute cartoon style, premium marketing studio layout.
```

## 저작권/IP 주의 사항

- 포켓몬, 산리오, 디즈니, 카카오프렌즈 등 특정 캐릭터를 닮은 인형 실루엣 금지.
- 실제 뽑기방 브랜드명, 간판, 로고, 상품 패키지 모사 금지.
- `인기 상품`은 캐릭터 굿즈가 아니라 캡슐, 박스, 원형 토큰, 추상 피규어 실루엣으로 대체한다.

## 다음 단계

- packaging은 코드네이티브 라인워크를 직접 구현하고 별도 사진 소재는 사용하지 않는다.
