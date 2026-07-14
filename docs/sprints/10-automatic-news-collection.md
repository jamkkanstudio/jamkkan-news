# Sprint 10 — 자동 뉴스 수집 운영화

## 상태

구현 완료 · 배포 검증 대기

## 목표와 범위

관리자 버튼 없이 최신 RSS 뉴스가 준비되도록 독립 실행 수집기와 GitHub Actions 예약 경로를 운영화합니다. 익명 공개 읽기, 관리자 수동 복구, JSON·Supabase 뉴스 동기화, 활성 사용자별 저장은 유지합니다. 기존 데이터 마이그레이션·삭제·소유권 변경, 유료 API, AI 요약과 다중 피드 순회는 제외합니다.

## 위험과 결정

- 초기 주기는 매시 3분부터 10분 간격입니다. 최신 피드 한 번만 요청해 하루 최대 144회로 제한하고 정각 혼잡을 피합니다. GitHub 예약은 지연될 수 있으므로 준실시간 목표이며 정확한 실행 시각을 보장하지 않습니다.
- 저장소는 공개이고 표준 GitHub-hosted runner를 사용합니다. 새 기사로 JSON이 바뀔 때만 커밋해 Streamlit 재배포와 Git 이력 증가를 줄입니다.
- 워크플로와 프로세스 잠금을 함께 사용합니다. 중간 실패 시 RSS 기사 ID 기반 UUID로 Supabase upsert를 재실행할 수 있고, JSON은 임시 파일에서 원자 교체합니다.
- 정규화 URL, 기사 ID, 최근 기사 지문으로 중복과 관리자가 삭제한 최근 기사의 재유입을 막습니다. 기사 지문은 최대 500개로 제한합니다.
- 자동 실행 주체 이메일은 Actions `ADMIN_EMAILS` 허용 목록과 별도 실행 주체 값이 일치해야 합니다. 상태는 마지막 성공 시각, 건수, 제한된 오류 코드만 기록하고 원문 예외·URL·비밀값은 기록하지 않습니다.
- 기존 JSON과 Supabase 행, owner-scoped 행은 구현 중 수정·삭제·자동 귀속하지 않습니다.

## 구현 결과

- RSS 호출에 20초 제한과 식별 가능한 User-Agent를 추가하고 RSS 기사 ID를 정규화 결과에 포함했습니다.
- 독립 수집 서비스와 `python -m scripts.collect_news` 진입점을 추가했습니다.
- Supabase 우선 upsert, 원자적 JSON 저장, 재실행 가능한 안정 UUID, URL·기사 지문 중복 방지, 동시 실행 잠금과 안전한 상태 기록을 추가했습니다.
- `Collect RSS news` 예약·수동 dispatch 워크플로를 추가하고 `contents: write`만 허용했습니다.
- 관리자 수집 화면은 자동 상태를 보여주고 기존 수동 등록을 예외 복구용으로 유지합니다.
- 같은 중요도의 뉴스는 최신 `created_at`을 먼저 표시합니다.

## 검증

- 표적 테스트: `python -m unittest -v test_auth_service test_rss test_supabase_service test_news_service test_news_collection_service test_ranking_service` — 35개 통과
- 최종 코드 변경 뒤 `python -m unittest discover -v` — 62개 통과
- `python -m compileall -q app.py components pages services scripts`와 workflow YAML 파싱 통과
- 로컬 Streamlit `/_stcore/health`와 `/` — HTTP 200
- `git diff --check`와 credential 패턴 검사 통과
- `events.json`, `growth.json`, `interest.json`, `news.json`, `settings.json`의 SHA-256이 Sprint 시작 기준과 일치하고 data diff가 없습니다.

## 배포 상태

코드 구현이 완료됐고 배포 검증 대기입니다. GitHub Actions Repository secrets 네 개의 안전한 UI 설정, 수동 dispatch, 예약 실행, 최신 뉴스 노출, 익명 읽기와 관리자 경계를 확인한 뒤 완료로 전환합니다.

## 다음 경계

운영 수집 빈도, 예약 지연, 기사 증가량과 재배포 횟수를 관찰한 뒤 피드별 분류 또는 보존 정책이 필요한지 별도 Sprint에서 결정합니다.
