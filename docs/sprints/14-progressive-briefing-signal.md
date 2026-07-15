# Sprint 14 — 새 브리핑 5개와 관심 성장 신호

## 상태

완료

## 목표와 범위

Sprint 13의 KST 당일 고정 후보와 첫 5개 품질·완료 의미를 유지하면서, 사용자가 원할 때만 이미 표시했거나 읽은 기사를 제외한 다음 최대 5개로 교체합니다. 카드 흐름을 `기사 읽기 → 도움이 됐어요 → 30초 투자 완료 → 새 기사`로 정리하고, 기사별 최소 도움 신호와 후보 소진 종료 상태를 추가합니다.

처음부터 대량 노출, 무한 스크롤, 고정 방해 CTA, 자동 관심사 변경, 체류시간 감시, 저장·공유, 관심도·성장도 자동 점수, 오늘의 도전, 월간 시야 지수는 제외했습니다. 익명 읽기, legacy 성장, 관리자 쓰기 경계, 자동 수집, JSON·Supabase 동기화, 사용자 격리와 기존 행을 보존했습니다.

## 감사·데이터 결정·롤백

- 기존 `events.json`과 owner-scoped `user_events`는 새 컬럼 없이 `article_helpful`을 수용합니다. 최소 필드는 `id`, `event_type`, `news_id`, 표시용 `category`·`title`, `seconds=0`, KST 발생시각입니다.
- 도움 신호는 기존 `article_read` 투자 통계에 섞이지 않고 관심사를 자동 변경하지 않습니다. 읽음은 기존 일별 `read_news_ids`를 그대로 사용합니다.
- 다음 묶음은 고정 후보 전체에서 동일 사건을 먼저 제거한 뒤 `표시한 ID ∪ 오늘 읽은 ID`를 제외합니다. 첫 5개만 기존 브리핑 완료 기준으로 남습니다.
- DB·JSON 스키마 마이그레이션, 기존 행 수정·삭제·소유권 할당이 없습니다. 코드 롤백만으로 기존 첫 5개 UI로 돌아갈 수 있고, 이미 기록된 `article_helpful` 행은 기존 분석 필터가 무시하므로 데이터 삭제가 필요 없습니다.

## 구현 결과

- 브리핑 관점을 `오늘의 TOP | 추천`으로 줄이고 카드에 `NEW | 읽음 | 도움됨` 상태를 표시했습니다.
- 현재 카드 아래의 명시적 버튼으로만 다음 최대 5개를 불러오며 기존 카드는 교체됩니다. 이후 묶음은 `NEW` 순번으로 구분합니다.
- 기사 카드 CTA 위계를 읽기, 도움 신호, 30초 완료 순으로 정리하고 완료를 카드의 주 행동으로 유지했습니다.
- 추가 후보가 없으면 오래된 기사나 같은 사건을 채우지 않는 짧은 종료 문구를 표시합니다.
- 도움 이벤트는 legacy JSON 또는 현재 owner의 Supabase 경로 하나로만 저장됩니다.

## 로컬 검증

- 표적 테스트: `python -m unittest -v test_ranking_service test_analytics_service test_growth_service test_personal_data_routing test_design_system` — 21개 통과
- 최종 코드 변경 후 전체 테스트: `python -m unittest discover -v` — 87개 통과
- Python 컴파일과 `.streamlit/config.toml` 파싱 통과
- 로컬 Streamlit `/_stcore/health`와 `/` — HTTP 200
- `git diff --check` 통과, 변경 diff 자격증명 패턴 0건, tracked `.env`·`.streamlit/secrets.toml` 0건
- `data/news.json`, `data/events.json`, `data/growth.json`, `data/interest.json`, `data/settings.json` 작업 diff 없음

## 배포 상태

코드 `dc55365`와 배포 대기 기록 `0e4b6b3`이 자동 수집 커밋 `22d38b7`을 보존한 채 `main`에 배포됐습니다. 운영 익명 홈에서 `오늘의 TOP | 추천`, 첫 5개 `NEW` 상태, `새 기사 5개` 교체와 별도 다음 5개, 카드 내부 `기사 읽기 → 도움이 됐어요 → 30초 투자 완료` 순서를 확인했습니다. 직접 관리 URL은 Google 로그인 요구로 차단됐고 브라우저 오류·경고는 0건이었습니다. 운영 데이터 쓰기 CTA는 검증 중 실행하지 않았습니다.

## 다음 경계

도움 신호를 관심사 제안에 사용할지는 최소 데이터, 정확도, 동의, 설명 가능성, 스키마와 롤백을 별도로 결정합니다. 관심사는 자동 변경하지 않고 사용자에게 제안만 허용합니다. 전체 사용자 데이터 초기화나 기존 소유권 변경도 별도 매핑·스냅샷·검증·롤백 승인 전에는 수행하지 않습니다.
