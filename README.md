# 잠깐. (Jamkkan)

30초 뉴스 브리핑과 성장 기록을 제공하는 Streamlit 앱입니다.

- Live: https://jamkkan-news.streamlit.app/
- Python: 3.12 권장
- Storage: JSON 운영 기준선 + Supabase 병행 저장

제품 방향은 [BRAND.md](BRAND.md)와 [PRINCIPLES.md](PRINCIPLES.md), 우선순위는 [ROADMAP.md](ROADMAP.md), 변경 이력은 [CHANGELOG.md](CHANGELOG.md)를 확인하세요.

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
python -m compileall -q app.py components pages services
```

## Storage operation

- `data/news.json`: 뉴스 운영 기준선
- `data/interest.json`: legacy 전역 관심 분야
- `data/settings.json`: legacy 전역 일일 목표
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

Sprint 07은 기존 데이터를 옮기지 않는 비활성 기반만 제공합니다. `supabase/user_data_foundation.sql`은 신규 빈 사용자 테이블, RLS, public 역할 차단을 정의합니다. 검토된 활성화 Sprint 전에는 운영 DB 적용이나 데이터 라우팅 전환을 하지 않습니다.

활성화 시 다음 배포 전용 값이 필요합니다.

```toml
USER_ID_PEPPER = "GENERATE_AT_LEAST_32_RANDOM_CHARACTERS"
SUPABASE_SECRET_KEY = "SERVER_ONLY_SUPABASE_SECRET_KEY"
```

legacy 이름 `SUPABASE_SERVICE_ROLE_KEY`도 지원합니다. 이 키들은 브라우저에 노출하지 말고 `USER_ID_PEPPER`를 백업하세요. Pepper를 바꾸면 모든 불투명 owner id가 달라지므로 검증된 owner-id 마이그레이션 없이 교체하면 안 됩니다.

## Project structure

```text
app.py                 Streamlit home
pages/                 management, settings, growth, analytics
components/            shared UI
services/              domain, authorization, storage
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
