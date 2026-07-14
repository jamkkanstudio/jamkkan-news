# Jamkkan Sprint Archive

Jamkkan의 Sprint 목표, 결정, 구현 결과와 검증 기록을 보관합니다.

채팅은 작업 과정이며, 이 문서와 Git 이력이 프로젝트의 공식 기록입니다.

## Sprints

| Sprint | 주제 | 상태 | 문서 |
| --- | --- | --- | --- |
| 01 | MVP와 성장 기반 구축 | 완료 | [01-mvp.md](01-mvp.md) |
| 02 | Supabase 신규 뉴스 병행 저장 | 완료 | [02-supabase-news-mirror.md](02-supabase-news-mirror.md) |
| 03 | 뉴스 수정·삭제 동기화 | 완료 | [03-news-update-delete-sync.md](03-news-update-delete-sync.md) |
| 04 | 사용자 상태 Supabase 마이그레이션 | 완료 | [04-user-state-supabase-migration.md](04-user-state-supabase-migration.md) |
| 05 | KST 날짜 기준 통일 | 완료 | [05-kst-date-standardization.md](05-kst-date-standardization.md) |
| 06 | Google 로그인 및 관리자 화면 보호 | 완료 | [06-google-login-admin-protection.md](06-google-login-admin-protection.md) |
| 07 | 사용자별 데이터 분리 설계 및 기반 구축 | 배포 검증 대기 | [07-user-data-isolation-foundation.md](07-user-data-isolation-foundation.md) |

## 상태

- `진행 중`: 구현 또는 검증 중
- `구현 완료 · 배포 검증 대기`: 로컬 완료, 아직 운영 확인 전
- `완료`: 최종 커밋 푸시와 운영 익명 읽기 검증까지 완료

## Sprint 기록 템플릿

각 기록은 필요한 항목만 짧게 작성합니다.

1. 상태와 목표
2. 포함/제외 범위
3. 위협 또는 실패 위험과 결정
4. 구현 결과
5. 테스트·컴파일·데이터 보존 검증
6. 커밋과 배포 확인
7. 사용자 조치와 다음 Sprint 경계

제품·아키텍처의 장기 결정은 `docs/PROJECT_CONTEXT.md`, 우선순위는 `ROADMAP.md`, release-relevant 변경은 `CHANGELOG.md`, 설정과 운영법은 `README.md`에만 기록합니다. Sprint 문서는 그 문서들을 반복하지 않고 이번 작업의 근거와 증거만 남깁니다.
