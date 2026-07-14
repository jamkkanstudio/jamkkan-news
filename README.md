<div align="center">

# 🌱 잠깐.

### **30초를, 나에게 투자하는 시간으로.**

![Version](https://img.shields.io/badge/version-v0.1.0-2E8B57)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Live-FF4B4B?logo=streamlit&logoColor=white)
![Status](https://img.shields.io/badge/status-Active-success)

**사람은 시간이 없어서 성장하지 못하는 것이 아니라,  
성장을 너무 거창하게 생각해서 시작하지 못한다고 믿습니다.**

잠깐.은

출근 전 30초,

커피를 기다리는 30초,

엘리베이터를 기다리는 30초를

**나에게 투자하는 시간**으로 바꾸는 성장 플랫폼입니다.

🌍 **Live Demo**

https://jamkkan-news.streamlit.app/

</div>

---

# 🌱 Why?

우리는 현대인이 바쁘다고 생각하지 않습니다.

우리는

**성장을 너무 거창하게 생각해서 시작하지 못한다고 생각합니다.**

사람들은

- 책은 1시간은 읽어야 하고
- 운동은 헬스장을 가야 하고
- 공부는 최소 30분은 해야 한다고 생각합니다.

그러다 결국

아무것도 하지 못합니다.

잠깐.은 다르게 생각합니다.

30초라도 충분합니다.

30초가 쌓이면

3분이 되고,

3분이 쌓이면

습관이 되고,

습관이 결국

한 사람을 성장시킨다고 믿습니다.

---

# ✨ Features

## 📰 오늘의 TOP5

오늘 가장 중요한 뉴스 5개를 제공합니다.

---

## 👤 나의 TOP5

관심 분야를 기반으로

나만의 브리핑을 제공합니다.

---

## 📥 RSS 뉴스 수집

RSS를 통해

최신 뉴스를 자동으로 가져옵니다.

---

## ✍ 자동 브리핑

기사를

짧고 읽기 쉬운 브리핑으로 제공합니다.

---

## 🌱 성장 시스템

기사를 읽을 때마다

나에게 투자한 시간이 기록됩니다.

---

## 📈 성장 대시보드

- 오늘 읽은 기사
- 누적 기사
- 투자 시간
- 연속 성장
- 주간 성장
- Asia/Seoul 기준의 일관된 오늘·주간 기록

을 확인할 수 있습니다.

---

## ✅ 브리핑 완료

오늘의 브리핑을 모두 읽으면

오늘은 충분합니다.

라는 메시지와 함께

하루를 마무리합니다.

우리는

사용자를 오래 붙잡지 않습니다.

---

# 🛠 Tech Stack

### Frontend

- Streamlit

### Backend

- Python

### Storage

- JSON (현재 기본 저장소)
- Supabase (뉴스와 사용자 상태 병행 저장)

> JSON을 기본 저장소로 보존하면서 관심 분야·일일 목표·일별 성장 기록을 Supabase에도 저장합니다.

### Version Control

- Git
- GitHub

---

# 📂 Project Structure

```text
jamkkan-news/
├── app.py
├── pages/          # 뉴스 관리·수집, 설정, 성장, 분석
├── components/     # 공통 UI 컴포넌트
├── services/       # 뉴스·RSS·성장·분석·Supabase 로직
├── data/           # 현재 JSON 데이터
├── docs/sprints/   # Sprint 목표·결정·완료 기록
├── test_*.py       # 자동 단위 테스트
└── *.md            # 제품 원칙, 로드맵, 변경 기록
```

Sprint별 작업 기록은 [Sprint Archive](docs/sprints/README.md)에서 확인할 수 있습니다.

---

# 🚀 Run

```bash
pip install -r requirements.txt

streamlit run app.py
```

---

# 🧭 Roadmap

## v0.1

✅ MVP Release

- RSS 뉴스 수집
- 오늘의 TOP5
- 나의 TOP5
- 성장 시스템
- 모바일 지원

---

## v0.2 (진행 중)

- ✅ Analytics
- ✅ Daily Goal
- ✅ 신규 뉴스 Supabase 병행 저장
- ✅ 뉴스 수정·삭제 Supabase 동기화
- ✅ 사용자 상태 Supabase 마이그레이션
- ✅ 성장·분석 날짜 기준 KST 통일
- Google Login
- 사용자 데이터 영구 저장

---

## v0.3

- AI Briefing
- AI Ranking
- AI Personalization

---

## v0.4

잠깐. Book

잠깐. Movie

잠깐. Fitness

잠깐. Finance

잠깐. Learning

---

## v1.0

Jamkkan Platform

30초 성장 플랫폼

---

# 🌱 Product Principles

우리는

사용자의 시간을 빼앗지 않습니다.

우리는

사용자가

자신에게 시간을 투자하도록 돕습니다.

우리는

무한 스크롤을 만들지 않습니다.

우리는

중독을 설계하지 않습니다.

우리는

사람이

매일 사용하는 기능만 만듭니다.

---

# 🌳 Vision

Jamkkan Studio는

뉴스 회사가 아닙니다.

콘텐츠 회사도 아닙니다.

우리는

사람의 성장을 돕는 회사입니다.

뉴스는

첫 번째 콘텐츠일 뿐입니다.

앞으로

📖 Book

🎬 Movie

💪 Fitness

📈 Finance

🧠 Learning

모든 콘텐츠를

30초 안에 전달하는

성장 플랫폼이 되는 것이 목표입니다.

---

# ❤️ Our Promise

우리는

사용자를 오래 붙잡지 않습니다.

오늘 충분히 성장했다면

기꺼이 보내드립니다.

> **오늘은 충분합니다.**

> **내일 다시 잠깐.**

---

# 🤝 About Jamkkan Studio

Jamkkan Studio는

사람이

어제보다 오늘

1% 더 성장하도록 돕는 회사를 꿈꿉니다.

우리는

콘텐츠를 만드는 회사가 아니라

사람의 성장을 만드는 회사를 지향합니다.

---

<div align="center">

## 🌱

### **잠깐의 시간이, 평생의 성장을 만든다.**

Made with ❤️ by **Jamkkan Studio**

</div>

---

## Google login configuration

Public reading works without authentication secrets. To enable protected management, configure this structure in an untracked `.streamlit/secrets.toml` or Streamlit Cloud app Secrets:

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

Register the exact same `redirect_uri` on the Google OAuth web client. Never place real IDs, secrets, cookie secrets, or administrator emails in code, Git, or logs.
