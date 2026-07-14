# Sprint 09 — 운영 개인 저장 활성화 및 실사용 검증

## 상태

진행 중 · 운영 검증 완료, 배포 기록 대기 · 2026-07-15

## 목표와 범위

Sprint 08의 기본 OFF 사용자별 저장 경로를 운영에서 스냅샷, 빈 스키마, 권한, 비밀값, 두 계정 격리, 실사용 순서로 활성화합니다. 기존 JSON과 legacy Supabase 행의 수정·삭제·자동 귀속, 기존 행 owner 매핑, AI·v0.4 확장과 자동 수집 구현은 제외합니다.

## 데이터 보존과 운영 결정

- `supabase/preflight_legacy_snapshot.sql`의 legacy 5개 테이블 행 수와 내용 지문을 Supabase private SQL 운영 기록에 저장했습니다. 원문 값은 코드와 Git에 기록하지 않았습니다.
- 신규 스키마 적용 뒤 같은 preflight를 다시 실행했고 적용 전후 행 수와 지문이 모두 일치했습니다.
- `supabase/user_data_foundation.sql`만 적용했습니다. legacy 테이블을 읽거나 수정하는 마이그레이션은 실행하지 않았습니다.
- 배포 Secrets에 서버 전용 키 별칭과 새 owner-id pepper를 저장했고 모든 사전 검증이 끝날 때까지 `USER_DATA_ENABLED = false`를 유지했습니다. 비밀값은 저장소나 로컬 파일에 기록하지 않았습니다.
- Google Cloud OAuth 웹 클라이언트와 Streamlit OIDC Secrets를 운영 UI에서 설정했습니다. OAuth 자격 증명과 실제 이메일은 코드와 Git에 기록하지 않았습니다.
- 두 계정 격리와 권한 검증을 모두 통과한 뒤에만 `USER_DATA_ENABLED = true`로 전환했습니다. 롤백은 플래그를 끄되 신규·기존 행을 보존하는 방식입니다.

## 운영 검증

- 적용 전 owner-scoped 테이블 4개가 존재하지 않음을 확인했습니다.
- 적용 후 `user_interests`, `user_settings`, `user_growth_daily`, `user_events`가 모두 0행임을 확인했습니다.
- 네 테이블의 RLS와 force RLS, `anon`·`authenticated` 차단, `service_role` CRUD 권한이 모두 기대값이었습니다.
- `replace_user_interests` RPC도 `anon`·`authenticated` 차단과 `service_role` 실행 권한이 기대값이었습니다.
- 배포 익명 홈과 legacy 성장 기록이 정상 렌더링됐고 브라우저 오류 로그는 0건이었습니다.
- 뉴스 관리 직접 접근은 익명 상태에서 차단됐습니다.
- 첫 번째 테스트 계정은 Google 로그인과 관리자 인식, 뉴스 관리 접근에 성공했습니다. 로그아웃 뒤 익명 공개 읽기와 legacy 성장 경로도 유지됐습니다.
- 서로 다른 두 테스트 계정에서 관심 분야와 목표가 서로 다르게 저장·재조회됐고, owner별 설정 행은 각각 독립된 하나의 집합으로 유지됐습니다.
- 계정 A의 기존 성장·분석 기록은 계정 B에서 보이지 않았습니다. 계정 B가 실제 뉴스 한 건을 완료한 뒤 `user_growth_daily`와 `user_events`는 각각 두 owner로 분리됐고 교차 읽기·쓰기는 발생하지 않았습니다.
- 서버 저장은 신뢰된 owner를 별도 인자로 받아 모든 조회에 owner 필터를 적용하며 payload의 owner 값은 무시합니다. 관련 회귀 테스트에서 payload owner 위조와 잘못된 owner 형식이 차단됐습니다.
- 계정 B의 완료 기록은 새로고침 뒤에도 오늘·누적 1개와 30초로 유지됐습니다.
- 최종 로그아웃 뒤 익명 사용자는 기존 legacy 목표·성장·관심 분야를 계속 조회했고 관리 페이지의 쓰기 기능은 노출되지 않았습니다.
- 최종 legacy 5개 테이블의 행 수와 내용 지문을 보호된 SQL 운영 기록에 다시 남겼습니다. 개인 데이터 실사용은 신규 owner 테이블에만 기록됐고 기존 행의 수정·삭제·자동 귀속은 실행하지 않았습니다.

## 테스트

- `python -m unittest -v test_identity_service test_user_data_service test_personal_data_routing` — 14개 통과
- 코드 변경이 없어 전체 테스트 재실행은 생략했습니다. Sprint 08의 마지막 코드 변경 뒤 전체 테스트는 통과 상태이며 이번 Sprint는 운영 스키마·Secrets·브라우저 검증과 문서만 변경했습니다.

## 배포 상태

운영 스키마, OIDC, 서버 전용 Secrets, owner-scoped 저장 활성화는 완료됐습니다. 문서 커밋을 `origin/main`에 배포한 뒤 공개 익명 읽기와 관리 경계를 한 번 더 확인하고 완료 커밋을 기록합니다.

## 다음 경계

다음 Sprint 후보는 관리자의 수동 실행 없이 최신 뉴스가 준비되도록 예약 수집, 중복 방지, 실패 관측을 갖춘 자동 뉴스 파이프라인입니다. 기존 개인 저장과 익명 읽기 경계는 그대로 유지합니다.
