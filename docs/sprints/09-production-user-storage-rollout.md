# Sprint 09 — 운영 개인 저장 활성화 및 실사용 검증

## 상태

진행 중 · 운영 OIDC와 두 계정 검증 대기 · 2026-07-15

## 목표와 범위

Sprint 08의 기본 OFF 사용자별 저장 경로를 운영에서 스냅샷, 빈 스키마, 권한, 비밀값, 두 계정 격리, 실사용 순서로 활성화합니다. 기존 JSON과 legacy Supabase 행의 수정·삭제·자동 귀속, 기존 행 owner 매핑, AI·v0.4 확장과 자동 수집 구현은 제외합니다.

## 데이터 보존과 운영 결정

- `supabase/preflight_legacy_snapshot.sql`의 legacy 5개 테이블 행 수와 내용 지문을 Supabase private SQL 운영 기록에 저장했습니다. 원문 값은 코드와 Git에 기록하지 않았습니다.
- 신규 스키마 적용 뒤 같은 preflight를 다시 실행했고 적용 전후 행 수와 지문이 모두 일치했습니다.
- `supabase/user_data_foundation.sql`만 적용했습니다. legacy 테이블을 읽거나 수정하는 마이그레이션은 실행하지 않았습니다.
- 배포 Secrets에 서버 전용 키 별칭과 새 owner-id pepper를 저장했고 `USER_DATA_ENABLED = false`를 유지했습니다. 비밀값은 저장소나 로컬 파일에 기록하지 않았습니다.

## 운영 검증

- 적용 전 owner-scoped 테이블 4개가 존재하지 않음을 확인했습니다.
- 적용 후 `user_interests`, `user_settings`, `user_growth_daily`, `user_events`가 모두 0행임을 확인했습니다.
- 네 테이블의 RLS와 force RLS, `anon`·`authenticated` 차단, `service_role` CRUD 권한이 모두 기대값이었습니다.
- `replace_user_interests` RPC도 `anon`·`authenticated` 차단과 `service_role` 실행 권한이 기대값이었습니다.
- 배포 익명 홈과 legacy 성장 기록이 정상 렌더링됐고 브라우저 오류 로그는 0건이었습니다.
- 뉴스 관리 직접 접근은 익명 상태에서 차단됐습니다.

## 대기 사유

운영 앱에는 Google OIDC 설정이 없어 로그인 기능이 읽기 전용 상태입니다. Google Cloud 계정은 최초 서비스 약관 동의와 프로젝트 선택 전 단계였으므로 이를 대신 수락하거나 OAuth 자격 증명을 임의 생성하지 않았습니다. 서로 다른 두 테스트 계정의 owner 분리와 교차 접근 차단을 실제 운영에서 검증할 수 없어 기능 플래그를 켜지 않았습니다.

## 안전한 사용자 조치와 다음 체크포인트

1. Google Cloud UI에서 서비스 약관을 직접 확인·동의하고 프로젝트를 만들거나 선택합니다.
2. OAuth 웹 클라이언트에 `https://jamkkan-news.streamlit.app/oauth2callback`을 등록합니다.
3. Streamlit App Settings의 Secrets 화면에 OAuth client id·secret, 새 cookie secret과 필요한 `ADMIN_EMAILS`를 직접 저장합니다. 실제 값은 채팅에 붙여넣지 않습니다.
4. 서로 다른 두 테스트 계정을 준비한 뒤 이 Sprint에서 로그인·로그아웃 호환과 owner 격리를 검증합니다.
5. 교차 읽기·쓰기 차단과 payload owner 위조 방지를 확인한 뒤에만 `USER_DATA_ENABLED`를 켜고 뉴스 읽기 → 완료 → 새로고침·재접속 유지 흐름을 검증합니다. 실패하면 플래그만 끄고 신규·기존 행은 보존합니다.

## 다음 경계

OIDC와 두 테스트 계정이 준비되면 같은 운영 기록에서 Sprint 09를 재개합니다. 완료 전에는 ROADMAP의 개인 저장·하루 사용 항목을 완료로 바꾸지 않으며, 자동 수집은 별도 Sprint 후보로 유지합니다.
