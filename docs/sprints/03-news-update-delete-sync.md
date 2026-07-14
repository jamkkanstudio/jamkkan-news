# Sprint 03 — 뉴스 수정·삭제 동기화

## 상태

완료 · 2026-07-15

## 목표

기존 JSON 데이터를 보존하면서 뉴스 수정과 삭제를 동일한 UUID로 Supabase에도 반영합니다.

## 범위

포함:

- 뉴스 수정 시 JSON 저장 후 Supabase `news` 테이블 upsert
- 뉴스 삭제 시 JSON 저장 후 Supabase `news` 테이블의 동일 UUID 삭제
- Supabase 실패 시 JSON 결과 유지와 화면 경고·서버 로그 제공
- 수정·삭제 동기화 자동 테스트

제외:

- 기존 JSON 뉴스 전체 이전
- 실패 작업 자동 재시도와 복구 큐
- 성장·관심 분야·설정 데이터 이전
- 로그인과 사용자별 데이터 분리

## 구현 결과

- 수정 시 기존 UUID와 생성 시각을 보존한 전체 뉴스 레코드 upsert
- 삭제 대상이 JSON에 있을 때만 Supabase 삭제 호출
- JSON 반영 성공과 Supabase 반영 실패를 관리 화면에서 구분
- 수정과 삭제를 각각 구현·검증·커밋

## 검증

- 자동 단위 테스트 10개 통과
- 수정 시 JSON·Supabase에 동일 UUID 레코드를 전달하는지 확인
- 삭제 시 JSON의 다른 뉴스를 보존하고 Supabase에 대상 UUID만 전달하는지 확인
- Supabase 예외와 존재하지 않는 삭제 대상 처리 확인
- Streamlit 배포 앱 정상 기동과 뉴스 관리 화면 렌더링 확인
- 운영 JSON 뉴스 3건 보존 확인(운영 데이터 수정·삭제 미실행)

## 주요 Git 기록

- `754a5c6` — 뉴스 수정 JSON·Supabase 동기화
- `43a2780` — 뉴스 삭제 JSON·Supabase 동기화
