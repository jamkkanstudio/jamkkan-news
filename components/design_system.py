from collections import Counter
from html import escape

import streamlit as st


CATEGORY_ICONS = {
    "경제": "📈",
    "정치": "🏛️",
    "사회": "👥",
    "국제": "🌍",
    "테크": "💻",
    "IT": "💻",
    "AI": "🤖",
    "반도체": "💾",
    "부동산": "🏠",
    "자동차": "🚗",
    "우주": "🚀",
    "미국주식": "🇺🇸",
    "기타": "📰",
}


def apply_design_system() -> None:
    """잠깐. 전 화면에 공통 디자인 토큰과 반응형 스타일을 적용합니다."""
    st.markdown(
        """
        <style>
        :root {
            --jm-ink: #18251d;
            --jm-muted: #657269;
            --jm-green: #1f6f4a;
            --jm-green-dark: #155437;
            --jm-green-soft: #e8f2ec;
            --jm-orange: #d98245;
            --jm-paper: #fbfcf9;
            --jm-line: #dfe7e1;
        }

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 78% 0%, #edf5ef 0, transparent 24rem),
                var(--jm-paper);
            color: var(--jm-ink);
        }

        [data-testid="stHeader"] {
            background: rgba(251, 252, 249, 0.88);
        }

        .block-container {
            max-width: 1080px;
            padding-top: 3rem;
            padding-bottom: 5rem;
        }

        h1, h2, h3, p {
            color: var(--jm-ink);
        }

        h1, h2, h3 {
            letter-spacing: -0.035em;
        }

        [data-testid="stSidebar"] {
            background: #f2f6f2;
            border-right: 1px solid var(--jm-line);
        }

        [data-testid="stSidebarNav"] {
            display: none;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] a {
            border-radius: 0.75rem;
            color: var(--jm-ink);
            padding: 0.55rem 0.65rem;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
            background: #e3ece5;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid var(--jm-line);
            border-radius: 1.1rem;
            box-shadow: 0 8px 24px rgba(28, 55, 38, 0.045);
        }

        [data-testid="stAlert"] {
            border-radius: 0.85rem;
            border-width: 1px;
        }

        .stButton > button,
        .stLinkButton > a,
        [data-testid="stFormSubmitButton"] > button {
            min-height: 2.75rem;
            border-radius: 0.75rem;
            font-weight: 700;
        }

        .stButton > button[kind="primary"] {
            background: var(--jm-green);
            border-color: var(--jm-green);
        }

        .stButton > button[kind="primary"]:hover {
            background: var(--jm-green-dark);
            border-color: var(--jm-green-dark);
        }

        [data-testid="stExpander"] {
            border-color: var(--jm-line);
            border-radius: 0.8rem;
        }

        [data-testid="stProgress"] > div > div > div > div {
            background-color: var(--jm-green);
        }

        .jm-page-intro {
            margin-bottom: 1.75rem;
        }

        .jm-kicker {
            color: var(--jm-green);
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            margin: 0 0 0.45rem;
            text-transform: uppercase;
        }

        .jm-page-intro h1 {
            font-size: clamp(2.15rem, 6vw, 3.6rem);
            line-height: 1.04;
            margin: 0;
        }

        .jm-page-intro p:last-child {
            color: var(--jm-muted);
            font-size: 1.02rem;
            line-height: 1.65;
            margin: 0.75rem 0 0;
            max-width: 42rem;
        }

        .jm-section-header {
            margin: 2.7rem 0 1rem;
        }

        .jm-section-header h2 {
            font-size: 1.45rem;
            margin: 0;
        }

        .jm-section-header p {
            color: var(--jm-muted);
            margin: 0.35rem 0 0;
        }

        .jm-topic-strip {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin: 0 0 1rem;
        }

        .jm-topic-chip {
            align-items: center;
            background: var(--jm-green-soft);
            border: 1px solid #d5e6d9;
            border-radius: 999px;
            color: var(--jm-green-dark);
            display: inline-flex;
            font-size: 0.84rem;
            font-weight: 750;
            gap: 0.35rem;
            padding: 0.4rem 0.7rem;
        }

        .jm-news-meta {
            align-items: center;
            display: flex;
            gap: 0.55rem;
            margin-bottom: 0.75rem;
        }

        .jm-rank {
            color: var(--jm-orange);
            font-size: 0.76rem;
            font-weight: 850;
            letter-spacing: 0.08em;
        }

        .jm-category {
            background: var(--jm-green-soft);
            border-radius: 999px;
            color: var(--jm-green-dark);
            font-size: 0.76rem;
            font-weight: 750;
            padding: 0.28rem 0.55rem;
        }

        .jm-news-copy h3 {
            font-size: 1.12rem;
            line-height: 1.38;
            margin: 0 0 0.65rem;
        }

        .jm-news-copy p {
            color: #46524a;
            display: -webkit-box;
            font-size: 0.92rem;
            line-height: 1.55;
            margin: 0 0 0.9rem;
            overflow: hidden;
            -webkit-box-orient: vertical;
            -webkit-line-clamp: 3;
        }

        .jm-personal-note {
            color: var(--jm-green);
            font-size: 0.78rem;
            font-weight: 700;
            margin-bottom: 0.7rem;
        }

        .jm-growth-head {
            align-items: baseline;
            display: flex;
            flex-wrap: wrap;
            gap: 0.3rem 0.65rem;
            justify-content: space-between;
        }

        .jm-growth-head strong {
            font-size: 1.1rem;
        }

        .jm-growth-head span,
        .jm-growth-summary {
            color: var(--jm-muted);
            font-size: 0.86rem;
        }

        .jm-growth-summary {
            margin: 0.25rem 0 0.8rem;
        }

        .jm-stat-grid {
            display: grid;
            gap: 0.75rem;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            margin: 0.5rem 0 1.25rem;
        }

        .jm-stat {
            background: #fff;
            border: 1px solid var(--jm-line);
            border-radius: 0.95rem;
            padding: 1rem;
        }

        .jm-stat span,
        .jm-stat small {
            color: var(--jm-muted);
            display: block;
        }

        .jm-stat strong {
            display: block;
            font-size: 1.65rem;
            margin: 0.2rem 0;
        }

        .jm-week-grid {
            display: grid;
            gap: 0.4rem;
            grid-template-columns: repeat(7, minmax(0, 1fr));
            margin: 0.75rem 0 1.25rem;
        }

        .jm-day {
            background: #fff;
            border: 1px solid var(--jm-line);
            border-radius: 0.8rem;
            min-width: 0;
            padding: 0.7rem 0.25rem;
            text-align: center;
        }

        .jm-day.active {
            background: var(--jm-green-soft);
            border-color: #c7dfcd;
        }

        .jm-day span,
        .jm-day small {
            color: var(--jm-muted);
            display: block;
            font-size: 0.72rem;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .jm-day strong {
            display: block;
            font-size: 1rem;
            margin: 0.3rem 0;
        }

        .jm-side-brand {
            color: var(--jm-ink);
            font-size: 1.5rem;
            font-weight: 900;
            letter-spacing: -0.05em;
            margin: 0.1rem 0 1rem;
        }

        @media (max-width: 640px) {
            .block-container {
                padding: 1.7rem 1rem 3.5rem;
            }

            .jm-page-intro {
                margin-bottom: 1.15rem;
            }

            .jm-page-intro h1 {
                font-size: 2.35rem;
            }

            .jm-page-intro p:last-child {
                font-size: 0.94rem;
                margin-top: 0.55rem;
            }

            .jm-section-header {
                margin-top: 2rem;
            }

            .jm-week-grid {
                gap: 0.25rem;
            }

            .jm-day {
                border-radius: 0.65rem;
                padding: 0.55rem 0.1rem;
            }

            .jm-day small {
                font-size: 0.64rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_intro(kicker: str, title: str, description: str) -> None:
    st.markdown(
        '<div class="jm-page-intro">'
        f'<p class="jm-kicker">{escape(kicker)}</p>'
        f'<h1>{escape(title)}</h1>'
        f'<p>{escape(description)}</p>'
        "</div>",
        unsafe_allow_html=True,
    )


def render_section_header(title: str, description: str) -> None:
    st.markdown(
        '<div class="jm-section-header">'
        f"<h2>{escape(title)}</h2>"
        f"<p>{escape(description)}</p>"
        "</div>",
        unsafe_allow_html=True,
    )


def get_topic_counts(
    news_list: list[dict],
    limit: int = 5,
) -> list[tuple[str, int]]:
    """기존 카테고리를 첫 등장 순서가 보존된 빈도순으로 요약합니다."""
    categories = [
        str(news.get("category", "기타")).strip() or "기타"
        for news in news_list
    ]
    return Counter(categories).most_common(limit)


def render_topic_strip(news_list: list[dict]) -> None:
    chips = []
    for category, count in get_topic_counts(news_list):
        icon = CATEGORY_ICONS.get(category, "📰")
        chips.append(
            '<span class="jm-topic-chip">'
            f"{escape(icon)} {escape(category)} · {count}"
            "</span>"
        )

    if chips:
        st.markdown(
            '<div class="jm-topic-strip" aria-label="오늘의 주제">'
            + "".join(chips)
            + "</div>",
            unsafe_allow_html=True,
        )


def render_stat_grid(stats: list[dict[str, str]]) -> None:
    cards = []
    for stat in stats:
        cards.append(
            '<div class="jm-stat">'
            f"<span>{escape(stat['label'])}</span>"
            f"<strong>{escape(stat['value'])}</strong>"
            f"<small>{escape(stat.get('detail', ''))}</small>"
            "</div>"
        )

    st.markdown(
        '<div class="jm-stat-grid">' + "".join(cards) + "</div>",
        unsafe_allow_html=True,
    )


def render_week_strip(days: list[dict[str, str | bool]]) -> None:
    day_cards = []
    for day in days:
        active_class = " active" if day.get("active") else ""
        marker = "🌱" if day.get("active") else "○"
        day_cards.append(
            f'<div class="jm-day{active_class}">'
            f"<span>{escape(str(day['label']))}</span>"
            f"<strong>{marker}</strong>"
            f"<small>{escape(str(day['value']))}</small>"
            "</div>"
        )

    st.markdown(
        '<div class="jm-week-grid">' + "".join(day_cards) + "</div>",
        unsafe_allow_html=True,
    )
