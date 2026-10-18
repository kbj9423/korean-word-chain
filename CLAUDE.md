# 끝말잇기 대결 (korean-word-chain)

AI와 하는 5단계 끝말잇기 웹 게임. 정적 사이트(`index.html` + `words.json`)를 GitHub Pages로 공개.
- 원격: https://github.com/kbj9423/korean-word-chain (브랜치 `main`, 공개 저장소)
- 사이트: https://kbj9423.github.io/korean-word-chain/
- 레이아웃(칠판 디자인)은 옆 폴더 `202610 korean word`(korean-dictionary)에서 가져왔다.
- 데이터 생성: `python scripts/build_words.py`. 원본 XML(`data/`, git 제외)은 spellcheck-ko/korean-dict-nikl에서 받고, 기초 어휘 등급·뜻과 기초사전 XML은 `../202610 korean word`에서 읽는다.
- 판정 사전(사람): 표준국어대사전 명사 + 우리말샘 방언·북한어·옛말 명사(고유명사 포함). AI는 단계별 범위 안에서만 쓰고 방언·북한어·옛말·고유명사는 쓰지 않는다(사용자 결정, 2026-10-18).
- 단계별 난이도 수치는 `index.html`의 `LEVELS`에 있다.

## 멀티 PC 작업 규칙
- 집/사무실 PC를 번갈아 작업한다. 코드 수정 전 `git fetch` → `git log HEAD..origin/main --oneline`으로 뒤처졌는지 확인하고, 뒤처졌으면 먼저 `git pull`.
- 커밋 안 된 로컬 변경이 있는 상태에서 pull이 필요하면 사용자에게 먼저 알린다.
- 작업이 끝나면 add → commit → push까지 마친다.
