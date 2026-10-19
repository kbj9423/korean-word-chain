# 끝말잇기 대결 (korean-word-chain)

AI와 하는 5단계 끝말잇기 웹 게임. 정적 사이트(`index.html` + `words.json`)를 GitHub Pages로 공개.
- 원격: https://github.com/kbj9423/korean-word-chain (브랜치 `main`, 공개 저장소)
- 사이트: https://kbj9423.github.io/korean-word-chain/
- 레이아웃(칠판 디자인)은 옆 폴더 `202610 korean word`(korean-dictionary)에서 가져왔다.
- 데이터 생성: `python scripts/build_words.py`. 원본 XML(`data/`, git 제외)은 spellcheck-ko/korean-dict-nikl에서 받고, 기초 어휘 등급·뜻과 기초사전 XML은 `../202610 korean word`에서 읽는다.
- 판정 사전(사람): 표준국어대사전 명사 + 우리말샘 방언·북한어·옛말 명사(고유명사 포함). AI는 단계별 범위 안에서만 쓰고 방언·북한어·옛말·고유명사는 쓰지 않는다(사용자 결정, 2026-10-18).
- 단계별 난이도 수치는 `index.html`의 `LEVELS`에 있다.

## 같이하기 (Firebase)
- 프로젝트: `arrowgame-e9ac7` (다른 게임들과 공유). 연결 코드는 `online.js`(같이하기를 누를 때만 불러옴).
- 컬렉션: `wordchain-rooms/{네 자리 방 코드}`. 익명 인증, 닉네임에 공용 비속어 필터(`app-config/profanity-words`) 적용. 전적은 저장하지 않는다(사용자 결정).
- 보안 규칙은 콘솔에서 직접 수정한다. `firestore.rules`는 콘솔 전체 규칙의 참고용 사본(2026-10-19 기준)이다. 다른 게임 규칙이 바뀌었을 수 있으니, 수정할 때는 사용자에게 콘솔의 현재 규칙을 받아 그 위에 고친다.
- 방 문서의 `expireAt`은 만든 지 1시간 뒤다. 프로젝트가 무료 요금제라 TTL은 못 쓴다(결제 계정 필요, 2026-10-19 확인). 대신 방을 만들 때 `expireAt`이 지난 방을 몇 개씩 지우고(보안 규칙에서 만료된 방은 누구나 삭제 허용), `join`은 지난 방을 없는 방으로 본다.

## 멀티 PC 작업 규칙
- 집/사무실 PC를 번갈아 작업한다. 코드 수정 전 `git fetch` → `git log HEAD..origin/main --oneline`으로 뒤처졌는지 확인하고, 뒤처졌으면 먼저 `git pull`.
- 커밋 안 된 로컬 변경이 있는 상태에서 pull이 필요하면 사용자에게 먼저 알린다.
- 작업이 끝나면 add → commit → push까지 마친다.
