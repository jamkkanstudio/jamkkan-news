# Sprint 04 — 사용자 상태 Supabase 마이그레이션

## 상태

완료 · 2026-07-15

## 목표

기존 JSON 데이터를 보존하면서 관심 분야, 일일 목표 설정, 일별 성장 기록을 JSON과 Supabase에 함께 저장하고, 기존 JSON 값을 운영 Supabase에 백필합니다.

## 범위

포함:

- 관심 분야 저장 시 `data/interest.json` 갱신 후 Supabase `interests` 전체 교체
- 일일 목표 저장 시 `data/settings.json` 갱신 후 Supabase `settings` upsert
- 기사 읽기 기록 시 `data/growth.json` 갱신 후 Supabase `growth_daily` upsert
- Supabase 실패 시 JSON 결과 보존과 화면 경고·서버 로그 제공
- 기존 관심 분야·일일 목표·일별 성장 기록 운영 백필
- 사용자 상태 동기화 자동 테스트

제외:

- `events` 동기화와 백필
- 기존 JSON 뉴스 전체 백필
- 로그인과 사용자별 데이터 분리
- 실패 작업 자동 재시도와 복구 큐
- JSON 데이터 삭제 또는 Supabase 단독 저장 전환

## 구현 결과

- 관심 분야 5개를 JSON에 먼저 저장한 뒤 Supabase 목록으로 교체
- `daily_goal_seconds`를 JSON에 먼저 저장한 뒤 동일 키의 JSONB 값으로 upsert
- 날짜별 기사 수, 투자 시간, 읽은 뉴스 UUID 목록을 JSON에 먼저 저장한 뒤 동일 날짜로 upsert
- 세 경로 모두 JSON 반영 성공과 Supabase 반영 실패를 구분할 수 있도록 반환값과 UI 메시지 구성
- `events` 동기화 실험은 기존 이벤트의 `news_id` 외래 키 제약을 확인한 뒤 되돌려 Sprint 범위에서 제외

## 운영 백필

2026-07-15에 Supabase SQL Editor에서 `interests`, `settings`, `growth_daily`만 포함한 단일 트랜잭션으로 실행했습니다.

- `interests`: 경제, 미국주식, AI, 반도체, IT — 5건
- `settings`: `daily_goal_seconds = 300` — 총 1건
- `growth_daily` 2026-07-14: 기사 7개, 210초, 읽은 뉴스 UUID 7개
- `growth_daily` 2026-07-15: 기사 3개, 90초, 읽은 뉴스 UUID 3개

트랜잭션 뒤 한 행의 검증 결과로 건수, 관심 분야 목록, 목표 값, 날짜별 기사 수·시간·UUID 목록이 JSON 원본과 일치함을 확인했습니다. `events`와 `news`는 쿼리에 포함하지 않았으며 로컬 JSON 파일도 변경하지 않았습니다.

## 검증

- 자동 단위 테스트 18개 통과
- 관심 분야 저장 순서가 JSON 후 Supabase인지 확인
- 일일 목표 저장 순서와 JSONB upsert 값을 확인
- 일별 성장 기록의 날짜, 기사 수, 초, UUID 목록 전달을 확인
- Supabase 예외 시 JSON 결과 보존과 실패 반환을 확인
- 운영 백필 후 `interests` 5건, `settings` 1건, `growth_daily` 2건 확인
- Streamlit 배포 앱 정상 기동 확인
- 설정 화면에서 관심 분야 5개와 목표 5분 선택 상태 확인
- 성장 화면에서 2일 연속, 누적 기사 10개·5분, 주간 화요일 7개·수요일 3개 렌더링 확인

## 배포 관찰 사항

배포 검증 시 서버의 `date.today()`가 KST보다 하루 느린 날짜를 반환해 성장 화면의 “오늘” 카드가 2026-07-14 기록인 기사 7개·3분 30초를 표시했습니다. 2026-07-15 기록은 주간 화면에 기사 3개로 정상 표시됐고 누적 값도 일치하므로 데이터 손실이나 마이그레이션 실패는 아닙니다. KST 기준 날짜 처리는 Sprint 04 범위에 포함하지 않고 후속 개선 항목으로 남깁니다.

## 주요 Git 기록

- `9b431ca` — 관심 분야 JSON·Supabase 동기화
- `49383dc` — 일일 목표 JSON·Supabase 동기화
- `fedd960` — 일별 성장 기록 JSON·Supabase 동기화
- `c7107be` — 범위를 벗어난 이벤트 동기화 실험 되돌림
