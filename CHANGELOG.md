# 🌱 CHANGELOG

모든 주요 변경 사항은 이 문서에 기록됩니다.

---

# Unreleased

> 다음 버전에 포함될 예정입니다.

---

# v0.2.0

**Release Date**

2026.07.15

## Authentication

- Added Streamlit native Google OIDC login and logout controls.
- Added a deployment-secret administrator email allowlist.
- Protected global news and settings writes at page and service boundaries.
- Preserved anonymous read-only operation when authentication is not configured.

## Privacy and data isolation

- Added an opaque HMAC-based owner identifier derived from the OIDC issuer and subject without storing raw identity claims.
- Added a separate owner-scoped Supabase schema with RLS enabled and direct anonymous/authenticated access revoked.
- Added server-only storage primitives that reject invalid owners, constrain reads by owner, and prevent payloads from overriding trusted ownership.
- Added one default-off feature flag that routes authenticated interests, goals, growth, and analytics together while failing closed on incomplete configuration.
- Added two-owner isolation, payload-owner rejection, backend-failure, and logout compatibility regression coverage.
- Activated owner-scoped production storage only after protected legacy snapshots, empty-schema and role checks, two-account isolation, and real read/refresh verification; all legacy rows remain preserved and unmapped.

## ✨ Added

### News Operations

- Added a 10-minute GitHub Actions RSS collector with workflow and process concurrency guards.
- Added stable article IDs, canonical URL and seen-article duplicate prevention, atomic JSON publishing, and retry-safe Supabase-first mirroring.
- Added administrator-visible last-success and safe failure-code status while retaining manual collection for recovery.
- Added KST attempt/success timestamps and a 30-minute collection-delay warning to administrator status.

### News Storage

- 신규 뉴스 JSON·Supabase 병행 저장
- 동일 UUID를 사용하는 Supabase upsert
- 병행 저장 성공·실패 자동 테스트
- 배포 환경 실제 저장 검증
- 뉴스 수정 JSON·Supabase 동기화
- 뉴스 삭제 JSON·Supabase 동기화
- 수정·삭제 동기화 성공·실패 자동 테스트

### Growth

- 오늘의 목표(Daily Goal)
- 목표 시간 설정 (30초 / 1분 / 2분 / 3분 / 5분)
- 목표 진행률 표시
- 목표 달성 안내 메시지
- 관심 분야 JSON·Supabase 병행 저장
- 일일 목표 JSON·Supabase 병행 저장
- 일별 성장 기록 JSON·Supabase 병행 저장
- 기존 관심 분야·일일 목표·일별 성장 기록 운영 백필
- 성장 기록 저장·조회와 연속 성장 날짜를 Asia/Seoul 기준으로 통일
- 성장 주간 화면과 분석 기간의 KST 날짜 경계 통일
- UTC/KST 날짜 경계 회귀 테스트 추가

### Analytics

- 나의 분석 페이지
- 이번 주와 전체 분석 기간 전환
- 요일별 투자 시간 및 주간 성장 기록
- 카테고리별 투자 비율 표시
- 가장 많이 읽은 분야 분석
- 사용자 뉴스 성향 분석

---

## 🏗 Infrastructure

- Supabase 프로젝트 생성
- PostgreSQL 데이터베이스 구축
- Streamlit ↔ Supabase 연결
- 데이터베이스 연결 테스트 완료
- Streamlit 운영용 Supabase secret 키 교체
- 운영용 DB 테스트 페이지 제거
- 서비스 클라우드 전환 준비

---

# v0.1.0

**Release Date**

2026.07.14

## ✨ Added

### Core

- RSS 뉴스 수집
- 뉴스 관리
- 오늘의 TOP5
- 나의 TOP5

### Personalization

- 관심분야 설정
- 개인 맞춤 뉴스

### Growth

- 성장 시스템
- 성장 배너
- 나의 성장 페이지
- 주간 성장 기록

### Reading

- 자동 브리핑
- 자동 중요도
- 브리핑 완료 화면

### Mobile

- 모바일 지원
- Streamlit 배포

---

## 📝 Notes

Jamkkan Studio의 첫 번째 MVP.

뉴스를 소비하는 서비스가 아니라

30초를 나에게 투자하는 성장 플랫폼의 첫 번째 버전입니다.

---

# Future

예정 기능은

ROADMAP.md를 참고하세요.
