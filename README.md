<div align="center">

# 🌱 잠깐.

### 30초를, 나에게 투자하는 시간으로.

![Version](https://img.shields.io/badge/version-v0.1.0-2E8B57)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Live-FF4B4B?logo=streamlit&logoColor=white)

**사람은 시간이 없어서 성장하지 못하는 것이 아니라,<br>
성장을 너무 거창하게 생각해서 시작하지 못한다고 믿습니다.**

[잠깐. 시작하기](https://jamkkan-news.streamlit.app/)

</div>

잠깐.은 출근 전, 커피를 기다리는 동안, 엘리베이터 안에서 생기는 짧은 시간을 나에게 투자하는 시간으로 바꾸는 서비스입니다.

우리는 뉴스를 많이 보여주지 않습니다. 오늘 꼭 알아야 할 뉴스와 나에게 중요한 뉴스만 짧게 전하고, 투자한 30초가 성장 기록으로 쌓이게 합니다.

## 잠깐.의 경험

- 🌍 **오늘의 TOP5** — 오늘 놓치지 말아야 할 뉴스
- 👤 **나의 TOP5** — 관심 분야를 반영한 개인 브리핑
- ✍ **30초 브리핑** — 핵심 내용과 중요한 이유
- 🌱 **성장 기록** — 읽은 기사, 투자 시간, 연속 성장
- 📊 **나의 분석** — 주간 기록과 관심 분야 흐름

> 우리는 사용자를 오래 붙잡지 않습니다.<br>
> 오늘 충분히 성장했다면 기꺼이 보내드립니다.

> **오늘은 충분합니다. 내일 다시 잠깐.**

제품의 전체 방향은 [BRAND.md](BRAND.md)와 [PRINCIPLES.md](PRINCIPLES.md), 우선순위는 [ROADMAP.md](ROADMAP.md), 변경 이력은 [CHANGELOG.md](CHANGELOG.md)를 확인하세요.

## Local setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

인증이나 Supabase 비밀값이 없어도 공개 뉴스 읽기와 기존 JSON 성장 기록 흐름은 동작합니다.

## Tests

```bash
python -m unittest discover -v
python -m compileall -q app.py components pages services scripts
```

## Storage operation

- `data/news.json`: 뉴스 운영 기준선
- `data/interest.json`: legacy 전역 관심 분야
- `data/settings.json`: legacy 전역 일일 목표와 전역 당일 브리핑 후보 스냅샷
- `data/growth.json`: legacy 익명 성장 기록
- `data/events.json`: legacy 익명 분석 이벤트
- Supabase: 뉴스와 legacy 사용자 상태의 병행 저장소

JSON 쓰기가 성공하고 Supabase 미러링이 실패하면 앱은 JSON 결과를 보존하고 경고합니다. 기존 JSON/Supabase 데이터를 삭제하거나 다시 백필하려면 별도 Sprint의 명시적 마이그레이션 계획이 필요합니다.

Supabase 병행 저장은 로컬의 untracked `.streamlit/secrets.toml` 또는 Streamlit Cloud Secrets에 설정합니다.

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_KEY = "SERVER_ONLY_KEY"
```

`SUPABASE_KEY`는 서버에서만 사용하고 브라우저 코드나 Git에 노출하지 마세요.

## Automatic news collection

Supabase Cron은 매시 7분부터 10분 간격으로 `.github/workflows/collect-news.yml`의 `workflow_dispatch`를 호출해 정치·경제·사회·국제 RSS를 통합 조회합니다. 한 분류 피드가 일시 실패해도 나머지 분류를 사용하고, 모든 분류가 실패할 때만 실행을 실패로 기록합니다. GitHub의 native `schedule` 이벤트가 생성되지 않는 운영 문제를 우회하며, 정확한 실행 시각이 아닌 준실시간 운영을 목표로 합니다. 새 기사만 안정적인 RSS 기사 ID와 정규화 URL로 중복을 제거해 실제 광역 카테고리와 유효 발행 시각을 Supabase에 먼저 upsert한 뒤 `data/news.json`을 원자 교체합니다.

중복을 통과한 신규 연합뉴스TV 기사만 공개 `/news/{기사ID}` 원문을 수집 시 한 번 읽습니다. 요청은 식별 가능한 User-Agent, 6초 제한, 512KB 상한, HTTPS 호스트·경로 allowlist를 사용합니다. 본문에서 앵커·기자 표기, 크레딧, 사진 설명, 제목 반복과 중복을 제거한 뒤 원문 문장 1~2개를 합계 140자 이내로 선택합니다. 원문 전문은 저장하지 않고 최종 `summary`만 기존 JSON·Supabase 필드에 저장하며, 추출·품질·timeout 오류는 기사별 RSS 설명으로 격리됩니다. 사용자 클릭은 외부 수집이나 요약을 실행하지 않습니다.

KST 당일 기사가 5개 모이면 즉시, 그렇지 않으면 오전 8시 이후 첫 후보군을 전역 `daily_briefing` 설정으로 한 번 고정합니다. 이 후보 ID는 Supabase `settings`와 `data/settings.json`에 같은 값으로 저장되며 기존 일일 목표 키는 유지됩니다. 이후 수집은 그날 후보군을 바꾸지 않고 다음 KST 날짜에만 새 스냅샷을 만듭니다. 워크플로는 `data/news.json` 또는 `data/settings.json`에 실제 변경이 있을 때만 `main`에 커밋합니다.

저장소의 **Settings → Secrets and variables → Actions**에서 다음 Repository secrets를 설정합니다. 실제 값은 코드, Git, Actions 로그, 채팅에 남기지 않습니다.

- `ADMIN_EMAILS`: Streamlit 배포와 같은 관리자 허용 목록을 쉼표로 구분
- `NEWS_AUTOMATION_ADMIN_EMAIL`: 위 허용 목록에 포함된 자동 실행 관리자 한 명
- `SUPABASE_URL`: 기존 Supabase 프로젝트 URL
- `SUPABASE_KEY`: 기존 서버 전용 뉴스 미러링 키

워크플로는 `contents: write`만 명시적으로 사용하고, 같은 수집 작업의 동시 실행을 막습니다. 마지막 시도·성공 시각과 제한된 실패 코드는 Supabase `settings`의 `news_collection_status`에 저장됩니다. 관리자 뉴스 수집 화면은 시각을 KST로 표시하고 마지막 성공 후 30분이 지나면 지연을 경고합니다. 실패한 실행은 다음 예약에서 다시 시도하며, RSS 원문 예외나 비밀값은 상태와 CLI 출력에 기록하지 않습니다.

운영 스케줄러는 `supabase/news_collection_scheduler.sql`로 적용하고 `supabase/verify_news_collection_scheduler.sql`로 확인합니다. GitHub fine-grained token은 `jamkkan-news` 저장소의 Actions 실행 권한만 허용하고 Supabase Vault의 `jamkkan_github_actions_token`에 저장합니다. 실제 토큰 값은 SQL 파일이나 SQL history에 직접 입력하지 않습니다. 롤백은 `supabase/rollback_news_collection_scheduler.sql`로 Job만 중지한 뒤 Vault UI에서 토큰을 제거합니다.

현재 토큰은 2026-10-13 만료이므로 2026-09-15에 교체를 시작합니다. 같은 저장소와 Actions 읽기·쓰기만 허용한 새 토큰을 만든 뒤 Vault UI에서 항목을 교체하고, 다음 예약 실행과 안전한 상태 기록을 확인한 다음에만 이전 토큰을 폐기합니다. 새 토큰 검증이 실패하면 아직 유효한 이전 토큰으로 Vault 항목을 되돌리고 원인을 확인합니다. 교체 과정에서도 토큰 값은 코드, Git, SQL history, 로그, 채팅에 입력하지 않습니다.

예외 복구가 필요하면 **Actions → Collect RSS news → Run workflow**로 수동 실행합니다. 기존 관리자 뉴스 수집 화면의 수동 등록도 복구용으로 유지됩니다. 공개 저장소의 표준 GitHub-hosted runner를 사용하므로 별도 유료 API는 추가되지 않지만, 예약 실행 지연과 사용량은 Actions 실행 기록에서 계속 관찰합니다.

## Google login and administrator access

Google 로그인은 선택 사항입니다. 설정하지 않으면 공개 읽기는 계속 동작하고 관리 화면은 차단됩니다.

```toml
ADMIN_EMAILS = ["admin@example.com"]

[auth]
redirect_uri = "https://YOUR_APP.streamlit.app/oauth2callback"
cookie_secret = "GENERATE_A_LONG_RANDOM_VALUE"

[auth.google]
client_id = "GOOGLE_CLIENT_ID"
client_secret = "GOOGLE_CLIENT_SECRET"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

Google OAuth 웹 클라이언트에 같은 `redirect_uri`를 등록하세요. 실제 ID, secret, cookie secret, 관리자 이메일은 코드·Git·로그에 남기지 않습니다.

## User data isolation rollout

사용자별 저장 코드는 `USER_DATA_ENABLED` 단일 플래그 뒤에 있으며 기본값은 꺼짐입니다. 꺼진 상태와 로그아웃 상태에서는 기존 JSON·Supabase 경로가 유지됩니다. 플래그가 켜진 로그인 요청은 관심 분야·목표·성장·분석을 모두 같은 owner 범위로 라우팅하며, 식별자나 서버 비밀키가 불완전하면 legacy 전역 데이터로 폴백하지 않습니다.

활성화 전 다음 순서를 지키세요.

1. `supabase/preflight_legacy_snapshot.sql` 결과를 보호된 운영 기록에 보관합니다.
2. `supabase/user_data_foundation.sql`로 신규 빈 테이블만 적용합니다.
3. `supabase/verify_user_data_foundation.sql`로 빈 테이블, RLS, `anon`/`authenticated` 차단과 `service_role` 권한을 확인합니다.
4. 배포 전용 비밀값을 설정하고 서로 다른 두 테스트 계정의 교차 읽기·쓰기가 차단되는지 확인합니다.
5. 마지막에만 `USER_DATA_ENABLED = true`로 바꾸고 재접속 후 영구 저장을 검증합니다.

배포 전용 값은 다음과 같습니다.

```toml
USER_ID_PEPPER = "GENERATE_AT_LEAST_32_RANDOM_CHARACTERS"
SUPABASE_SECRET_KEY = "SERVER_ONLY_SUPABASE_SECRET_KEY"
USER_DATA_ENABLED = false
```

legacy 이름 `SUPABASE_SERVICE_ROLE_KEY`도 지원합니다. 이 키들은 브라우저에 노출하지 말고 `USER_ID_PEPPER`를 백업하세요. Pepper를 바꾸면 모든 불투명 owner id가 달라지므로 검증된 owner-id 마이그레이션 없이 교체하면 안 됩니다. 기존 행은 이 절차에서 수정·삭제·자동 귀속하지 않습니다. 롤백은 플래그만 끄며 신규·기존 행은 유지합니다.

## Project structure

```text
app.py                 Streamlit home
pages/                 management, settings, growth, analytics
components/            shared UI
services/              domain, authorization, storage
scripts/               independent operational entry points
.github/workflows/      scheduled operations
supabase/              reviewed SQL foundations
data/                  legacy operational JSON
docs/PROJECT_CONTEXT.md durable architecture context
docs/sprints/          Sprint decisions and verification
test_*.py              unittest coverage
```

Sprint 기록은 [docs/sprints/README.md](docs/sprints/README.md)에서 확인합니다.

## Deployment verification

`main` 푸시 뒤 다음을 확인합니다.

1. 익명 홈이 기존 뉴스를 렌더링합니다.
2. 기사 브리핑과 legacy 성장 기록 흐름이 비밀값 없이 동작합니다.
3. 관리 화면은 인증 미설정 또는 비관리자에게 차단됩니다.
4. 브라우저 오류 로그에 앱 예외나 비밀값이 없습니다.
