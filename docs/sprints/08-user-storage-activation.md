# Sprint 08 — 사용자별 저장 활성화 및 격리 검증

## 상태

구현 완료 · 배포 검증 대기

## 목표와 범위

Sprint 07의 owner-scoped 저장 기반을 검증 가능한 순서로 연결하고, 운영 조건이 없으면 기능을 켜지 않은 채 안전한 롤아웃 경계까지 완성합니다. 기존 JSON과 legacy Supabase 행의 수정·삭제·자동 귀속, 유료 API, AI·v0.4 확장은 제외합니다.

## 데이터 보존과 운영 조건

2026-07-15 시작 시 로컬 JSON의 행 수와 SHA-256을 기록했습니다.

| 파일 | 행 수 | SHA-256 |
| --- | ---: | --- |
| `events.json` | 3 | `f30582e3d47884d1dc7d7b4054154c8b6d295b1affe4840679d82f28eeee34ee` |
| `growth.json` | 2일 | `9136600d6d365b6572212dd0657dffdd21c78f2deed2d3eb757db424c23b80ee` |
| `interest.json` | 5 | `73b3160d2324ad0a58a7c7563730c4ac93428a0354d4fe0e1ebd017bab9c6abd` |
| `news.json` | 3 | `e9bbdb89fd44142bf03407412229afa8a2bd10d4564809d17dd882d4e04af6c9` |
| `settings.json` | 1 | `9bc2e28cf838446a91a16a1ec04e09fa98d93130bba94338293eb6abe4d97a96` |

로컬에는 운영 비밀 파일, Supabase CLI, DB 접속 수단이 없었습니다. 따라서 legacy Supabase `interests/settings/growth_daily/events/news`의 현재 행 수·내용 지문 저장, 신규 스키마 적용, 실제 역할별 접근 검증은 수행하지 않았습니다. 대신 변경 없는 사전 스냅샷 SQL과 적용 후 권한·빈 테이블 검증 SQL을 제공하고 `USER_DATA_ENABLED`는 기본 OFF로 유지했습니다.

## 구현 결과

- 하나의 `USER_DATA_ENABLED` 플래그가 로그인 사용자의 관심 분야·목표·성장·분석을 같은 불투명 owner 범위로 함께 전환합니다.
- 플래그가 켜진 로그인 요청은 claim, pepper 또는 서버 Supabase 설정이 불완전하면 예외로 중단되고 legacy 전역 데이터로 폴백하지 않습니다.
- 로그아웃 또는 플래그 OFF 상태에서는 공개 읽기와 legacy 성장 기록 경로가 그대로 동작합니다.
- 설정 화면은 개인 라우팅이 활성화된 로그인 사용자에게 자기 데이터 저장을 허용하고, legacy 전역 쓰기는 기존 관리자 경계를 유지합니다.
- 사용자 성장 일별 행을 기존 화면 계약의 누적·연속 기록으로 변환하며, 분석 이벤트 시간 필드도 기존 KST 분석 계약과 호환합니다.
- `supabase/user_data_foundation.sql`은 `PUBLIC` 권한도 명시적으로 회수합니다. 읽기 전용 preflight와 post-apply 검증 SQL을 추가했습니다.

## 검증

- 관련 최소 테스트: 32개 통과
- 전체 `python -m unittest discover -v`: 51개 통과
- 서로 다른 두 owner의 관심 분야·목표·성장·분석 분리와 교차 읽기 차단, owner 없는 공개 API를 통한 교차 쓰기 방지 확인
- growth/event payload owner 위조 무시, 잘못된 owner 선차단, backend 설정 실패 시 legacy 관심 분야 비노출 확인
- 로그아웃 후 기능 플래그가 켜져 있어도 legacy 성장 기록 호환 확인
- Python compilation, `git diff --check`: 통과
- 비밀 패턴과 tracked `.env`/`.streamlit/secrets.toml`: 0건
- 로컬 Streamlit 비밀값 없는 smoke: health HTTP 200 `ok`, root HTTP 200
- 보호된 `data/*.json`: 변경 0건, 종료 지문은 시작 지문과 동일

## 배포

첫 구현 커밋과 익명 배포 검증 전입니다. 운영 사용자 데이터 기능은 비활성 상태입니다.

## 사용자 조치

1. 운영에서 `supabase/preflight_legacy_snapshot.sql` 결과를 보호된 위치에 보관합니다.
2. `user_data_foundation.sql` 적용 후 `verify_user_data_foundation.sql`의 모든 권한 boolean과 신규 테이블 0행을 확인합니다.
3. Streamlit 배포 Secrets에 백업된 `USER_ID_PEPPER`, `SUPABASE_SECRET_KEY`, 초기 `USER_DATA_ENABLED = false`를 설정합니다. 값은 공유하거나 로그에 남기지 않습니다.
4. 서로 다른 두 테스트 계정으로 owner 분리, 교차 읽기·쓰기 차단, 로그아웃 호환을 확인한 뒤에만 플래그를 켭니다.

## 다음 경계

운영 조건을 갖춰 플래그를 활성화하고 실제 뉴스 읽기 → 재접속 후 개인 기록 유지의 하루 사용 테스트를 완료합니다. 기존 데이터의 owner 매핑과 이관은 별도 승인·스냅샷·롤백 Sprint 전에는 수행하지 않습니다.
