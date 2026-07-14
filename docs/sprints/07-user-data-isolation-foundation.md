# Sprint 07 — 사용자별 데이터 분리 설계 및 기반 구축

## 상태

완료 · 2026-07-15

## 목표

Google OIDC 다음 보안 경계인 개인 데이터 소유권을 정의하고, 기존 전역 JSON/Supabase 데이터를 변경하거나 임의의 사용자에게 귀속하지 않은 채 안전한 식별자·스키마·서버 저장 기반을 준비합니다.

## 위협 모델

- 로그인 사용자가 다른 사용자의 관심 분야, 목표, 성장 기록, 분석 이벤트를 읽거나 덮어쓰는 수평 권한 상승
- 이메일, 이름, 사진 또는 원본 OIDC subject를 불필요하게 영구 저장하는 개인정보 확대
- 브라우저나 publishable key가 사용자 테이블에 직접 접근하는 경로
- service/secret key가 RLS를 우회한다는 사실을 놓치고 서버 쿼리에서 소유자 필터를 빠뜨리는 문제
- 요청 payload의 `owner_id`를 신뢰해 다른 사용자에게 기록을 삽입하는 문제
- 소유자를 증명할 수 없는 기존 전역 데이터를 최초 로그인 사용자에게 자동 귀속하는 오마이그레이션
- 소유자 HMAC pepper 분실·무계획 교체로 모든 기존 사용자 키가 달라지는 문제
- 인증·Supabase 설정이 없는 공개 읽기와 기존 성장 기록 흐름의 회귀

## 결정

- 사용자 소유권의 입력은 OIDC `(iss, sub)` 두 claim으로 제한합니다. 이메일은 관리자 allowlist 확인과 화면 표시에만 사용하고 개인 데이터 키로 저장하지 않습니다.
- `(iss, sub)`는 배포 전용 `USER_ID_PEPPER`로 HMAC-SHA256 처리해 `usr_<64 hex>` 형식의 불투명 키로 만듭니다. claim 원문과 매핑 테이블은 저장하지 않습니다.
- 익명 사용자는 기존 JSON/Supabase 경로를 계속 사용합니다. 로그인 사용자의 claim 또는 pepper가 불완전할 때는 전역 데이터로 폴백하지 않는 실패 폐쇄 모델을 채택합니다.
- 신규 `user_interests`, `user_settings`, `user_growth_daily`, `user_events` 테이블은 기존 테이블과 분리합니다. 기존 행을 조회·수정·삭제·백필하는 SQL은 포함하지 않습니다.
- 신규 테이블은 RLS를 활성화하고 `anon`/`authenticated` 권한을 회수합니다. Streamlit 서버의 별도 secret/service-role key만 접근하며, 이 키는 브라우저에 전달하지 않습니다.
- service-role은 RLS를 우회하므로 실제 사용자 격리는 서버 서비스 경계가 강제합니다. 모든 조회는 검증된 `owner_id` 조건을 포함하고, 쓰기는 payload의 소유자 값을 버리고 신뢰된 인자로 덮어씁니다.
- 관심 분야 전체 교체는 한 소유자의 행만 대상으로 하는 권한 제한 RPC 안에서 원자적으로 처리합니다.
- 이번 Sprint에서는 스키마를 운영 DB에 적용하거나 화면·기존 서비스의 데이터 라우팅을 전환하지 않습니다. 실제 이관도 수행하지 않습니다.

## 구현 결과

- `services/identity_service.py`: 익명/사용자 scope 결정, 불투명 owner id 생성, 로그인 상태의 불완전한 설정 실패 폐쇄
- `services/user_data_service.py`: 서버 비밀키 전용 클라이언트, owner 형식 검증, 관심 분야·설정·성장·이벤트의 owner 강제 읽기/쓰기
- `supabase/user_data_foundation.sql`: 네 개의 신규 빈 테이블, 복합 기본 키, 검증 제약, RLS, public 역할 권한 회수, 원자적 관심 분야 교체 RPC
- 보안 회귀 테스트: 결정적이지만 불투명한 식별자, issuer 경계, 비밀값 누락 실패, 잘못된 owner 사전 거부, owner 필터, 복합 upsert 키, payload owner 무시

## 개발 프로세스 개선

- `AGENTS.md`에 선택적 코드 탐색, 최소 테스트 후 최종 전체 테스트 1회, 작은 커밋, 배포 전 완료 표시 금지를 명문화했습니다.
- 문서 역할을 분리했습니다. README는 짧은 사용자용 브랜드 소개와 설정·운영, ROADMAP은 결과 상태, CHANGELOG는 release-relevant 변경, PROJECT_CONTEXT는 장기 결정, Sprint 기록은 작업 근거와 증거만 담당합니다.
- README의 감성적인 첫인상과 핵심 경험은 유지하되 전체 비전·원칙·로드맵의 반복은 제거하고 `BRAND.md`, `PRINCIPLES.md`, `ROADMAP.md`로 연결했습니다.
- Sprint archive에 상태 정의와 간결한 기록 템플릿을 추가해 다음 Sprint의 중복 작성과 조기 완료 표시를 방지했습니다.

## 기존 데이터 호환성

- `data/*.json`은 변경하지 않았습니다.
- 기존 Supabase `interests`, `settings`, `growth_daily`와 다른 운영 테이블은 변경하지 않았습니다.
- 앱의 현재 공개 읽기·성장 기록 경로는 그대로이므로 인증 및 신규 비밀값 없이 동작합니다.
- 기존 전역 데이터는 소유자가 확인되지 않은 legacy anonymous 데이터로 유지합니다.

## 다음 활성화 Sprint의 필수 순서

1. 기존 JSON과 Supabase 테이블의 행 수·키·내용 체크섬을 스냅샷하고 복구 지점을 만듭니다.
2. 신규 빈 스키마만 적용한 뒤 `anon`/`authenticated` 접근 거부와 서버 전용 접근을 검증합니다.
3. 배포에 `USER_ID_PEPPER`와 `SUPABASE_SECRET_KEY`를 설정하고 비밀값 자체는 출력하지 않습니다.
4. 서로 다른 두 테스트 계정으로 owner id 분리, 교차 읽기·쓰기 차단, 로그아웃 후 익명 호환성을 검증합니다.
5. 명시적 기능 플래그로 로그인 사용자의 관심 분야·목표·성장·분석 라우팅을 함께 전환합니다. 일부 데이터만 섞어 전환하지 않습니다.
6. 기존 전역 데이터는 소유권 매핑이 승인된 경우에만 별도 트랜잭션으로 복사하고 원본은 유지합니다. 자동 귀속하지 않습니다.
7. 롤백은 라우팅 플래그를 끄는 방식으로 수행하고 신규·기존 행을 삭제하지 않습니다.

## 검증

- `python -m unittest discover -v`: 45개 통과
- Python compilation: 통과
- Local Streamlit smoke test without auth/user-data secrets: health HTTP 200 `ok`, root HTTP 200
- 비밀값 패턴 검사: 실제 비밀값 없음, README의 명시적 placeholder만 확인
- `git diff --check`: 통과
- 기존 `data/` 파일: 변경 없음

## 배포

- 운영 스키마 적용과 사용자 라우팅 활성화는 의도적으로 다음 Sprint로 분리했습니다.
- `27d06ed`와 `8a609be`를 `origin/main`에 푸시했습니다.
- 익명 홈에서 기존 뉴스와 성장 요약이 렌더링됐고, 성장 페이지에서 2일 연속·누적 10개·5분 기록이 유지됐습니다.
- 뉴스 관리 직접 접근은 인증 미설정 상태에서 차단됐고 세 검증 경로의 브라우저 오류 로그는 비어 있었습니다.

## 사용자 조치

- 이번 Sprint에 필요한 조치는 없습니다.
- `supabase/user_data_foundation.sql`, `USER_ID_PEPPER`, `SUPABASE_SECRET_KEY`는 다음 활성화 Sprint의 검증 순서에 따라 함께 적용합니다.

## 주요 커밋

- `27d06ed` — 사용자 소유권 식별자, 서버 저장 어댑터, RLS 스키마, 보안 테스트
- `8a609be` — 개발 프로세스 최적화, 문서 역할 정리, Sprint 기록
