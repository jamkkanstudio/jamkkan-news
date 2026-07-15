import re
from html.parser import HTMLParser
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from services.summarizer import create_brief


ARTICLE_TIMEOUT_SECONDS = 6
ARTICLE_MAX_BYTES = 512_000
ARTICLE_SUMMARY_MAX_LENGTH = 140
MIN_ARTICLE_TEXT_LENGTH = 120
MIN_ARTICLE_SENTENCES = 3
ARTICLE_USER_AGENT = (
    "JamkkanNewsCollector/1.0 "
    "(+https://jamkkan-news.streamlit.app/)"
)
ALLOWED_ARTICLE_HOSTS = {"www.yonhapnewstv.co.kr"}
ALLOWED_ARTICLE_PATH = re.compile(r"^/news/[A-Za-z0-9_-]+/?$")

_ROLE_PREFIX = re.compile(r"^\s*\[(?:앵커|기자)\]\s*")
_CREDIT_LINE = re.compile(
    r"^\[(?:영상취재|영상편집|그래픽|뉴스리뷰|취재|편집)[^\]]*\]$"
)
_PHOTO_LINE = re.compile(
    r"^\[[^\]]*(?:사진|자료사진|제공|재판매|DB금지)[^\]]*\]$",
    re.IGNORECASE,
)
_INLINE_PHOTO_CAPTION = re.compile(
    r"\[[^\]]*(?:사진|자료사진|제공|재판매|DB금지)[^\]]*\]",
    re.IGNORECASE,
)
_REPORTER_SIGNOFF = re.compile(
    r"^(?:연합뉴스TV\s+)?[가-힣·]{2,12}(?:\s+기자)?입니다[.!]?$"
    r"|^(?:연합뉴스TV\s+)?[가-힣·]{2,12}\s+기자[.!]?$"
)
_SPEAKER_PREFIX = re.compile(r'^<[^>]{2,80}>\s*')
_EMAIL = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
_NOISE_PHRASES = (
    "기사문의 및 제보",
    "무단 전재",
    "재배포",
    "저작권자",
    "copyright",
)
_REPORTING_TERMS = (
    "밝혔",
    "발표",
    "결정",
    "확인",
    "집계",
    "나타났",
    "전망",
    "증가",
    "감소",
    "상승",
    "하락",
    "돌파",
    "넘어",
)
_TITLE_STOPWORDS = {
    "관련",
    "대한",
    "오늘",
    "최근",
    "올해",
    "정부",
    "기자",
}


class ArticleExtractionError(RuntimeError):
    """본문 추출이 안전 기준을 충족하지 못한 경우입니다."""


class _YonhapArticleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._capture_depth = 0
        self._finished = False
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if self._finished:
            return
        if self._capture_depth:
            if tag in {"br", "p"}:
                self._parts.append("\n")
            if tag not in {"br", "hr", "img", "input", "meta", "link"}:
                self._capture_depth += 1
            return
        if tag != "div":
            return
        classes = ""
        for name, value in attrs:
            if name == "class" and value:
                classes = value
                break
        if "article-body-text" in classes.split():
            self._capture_depth = 1

    def handle_startendtag(self, tag: str, attrs) -> None:
        if self._capture_depth and tag == "br":
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if not self._capture_depth:
            return
        if tag in {"br", "hr", "img", "input", "meta", "link"}:
            return
        if tag in {"p", "div"}:
            self._parts.append("\n")
        self._capture_depth -= 1
        if self._capture_depth == 0:
            self._finished = True

    def handle_data(self, data: str) -> None:
        if self._capture_depth and not self._finished:
            self._parts.append(data)

    def text(self) -> str:
        return "".join(self._parts)


def _validate_article_url(url: str) -> None:
    parts = urlsplit(str(url).strip())
    if (
        parts.scheme.lower() != "https"
        or parts.hostname not in ALLOWED_ARTICLE_HOSTS
        or parts.port not in (None, 443)
        or not ALLOWED_ARTICLE_PATH.fullmatch(parts.path)
        or parts.username
        or parts.password
    ):
        raise ArticleExtractionError("article_url_not_allowed")


def fetch_article_html(url: str) -> str:
    """허용된 공개 기사 HTML만 제한된 크기와 시간으로 한 번 읽습니다."""
    _validate_article_url(url)
    request = Request(
        url,
        headers={
            "User-Agent": ARTICLE_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    try:
        with urlopen(request, timeout=ARTICLE_TIMEOUT_SECONDS) as response:
            _validate_article_url(response.geturl())
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type.lower():
                raise ArticleExtractionError("article_content_type_invalid")
            content_length = response.headers.get("Content-Length")
            if content_length:
                try:
                    if int(content_length) > ARTICLE_MAX_BYTES:
                        raise ArticleExtractionError("article_too_large")
                except ValueError:
                    raise ArticleExtractionError(
                        "article_content_length_invalid"
                    ) from None
            body = response.read(ARTICLE_MAX_BYTES + 1)
            if len(body) > ARTICLE_MAX_BYTES:
                raise ArticleExtractionError("article_too_large")
            charset = response.headers.get_content_charset() or "utf-8"
    except ArticleExtractionError:
        raise
    except (OSError, ValueError) as error:
        raise ArticleExtractionError("article_fetch_failed") from error

    try:
        return body.decode(charset)
    except (LookupError, UnicodeDecodeError) as error:
        raise ArticleExtractionError("article_decode_failed") from error


def extract_article_text(html_text: str) -> str:
    """연합뉴스TV 공개 기사 본문 컨테이너의 텍스트만 추출합니다."""
    parser = _YonhapArticleParser()
    try:
        parser.feed(html_text)
        parser.close()
    except (TypeError, ValueError) as error:
        raise ArticleExtractionError("article_parse_failed") from error
    text = parser.text().strip()
    if not text:
        raise ArticleExtractionError("article_body_missing")
    return text


def _canonical_text(text: str) -> str:
    return re.sub(r"[^0-9A-Za-z가-힣]", "", text).lower()


def _is_noise_line(line: str) -> bool:
    lowered = line.lower()
    return bool(
        not line
        or _CREDIT_LINE.fullmatch(line)
        or _PHOTO_LINE.fullmatch(line)
        or _REPORTER_SIGNOFF.fullmatch(line)
        or _EMAIL.search(line)
        or any(phrase in lowered for phrase in _NOISE_PHRASES)
    )


def clean_article_text(text: str, *, title: str = "") -> str:
    """역할·크레딧·사진 설명·중복·제목 반복을 제거합니다."""
    title_key = _canonical_text(title)
    cleaned_lines: list[str] = []
    seen: set[str] = set()

    for raw_line in re.split(r"[\r\n]+", text):
        line = re.sub(r"\s+", " ", raw_line).strip()
        line = _ROLE_PREFIX.sub("", line).strip()
        line = _SPEAKER_PREFIX.sub("", line).strip()
        line = _INLINE_PHOTO_CAPTION.sub("", line).strip()
        if _is_noise_line(line):
            continue
        key = _canonical_text(line)
        if not key or key == title_key or key in seen:
            continue
        seen.add(key)
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def _sentences(text: str, *, title: str = "") -> list[str]:
    title_key = _canonical_text(title)
    results: list[str] = []
    seen: set[str] = set()
    for block in text.splitlines():
        for value in re.split(r"(?<=[.!?。])\s+", block):
            sentence = re.sub(r"\s+", " ", value).strip()
            key = _canonical_text(sentence)
            if (
                len(sentence) < 20
                or len(sentence) > ARTICLE_SUMMARY_MAX_LENGTH
                or not key
                or key == title_key
                or key in seen
                or _is_noise_line(sentence)
            ):
                continue
            seen.add(key)
            results.append(sentence)
    return results


def _tokens(text: str) -> set[str]:
    return {
        token.lower()
        for token in re.findall(r"[0-9A-Za-z가-힣]{2,}", text)
        if token.lower() not in _TITLE_STOPWORDS
    }


def _sentence_score(sentence: str, index: int, title_tokens: set[str]) -> int:
    tokens = _tokens(sentence)
    score = max(0, 5 - index)
    score += 4 * len(tokens & title_tokens)
    score += 2 * sum(term in sentence for term in _REPORTING_TERMS)
    if re.search(r"\d", sentence):
        score += 2
    if sentence.endswith(("습니다.", "했습니다.", "됐습니다.")):
        score += 1
    if sentence.endswith("?") or "있는데요" in sentence:
        score -= 2
    return score


def _too_similar(first: str, second: str) -> bool:
    first_tokens = _tokens(first)
    second_tokens = _tokens(second)
    union = first_tokens | second_tokens
    if not union:
        return True
    return len(first_tokens & second_tokens) / len(union) >= 0.65


def create_extractive_brief(
    text: str,
    *,
    title: str = "",
    max_length: int = ARTICLE_SUMMARY_MAX_LENGTH,
) -> str | None:
    """원문 문장만 점수화해 1~2개의 결정적 브리핑을 만듭니다."""
    cleaned = clean_article_text(text, title=title)
    if len(cleaned) < MIN_ARTICLE_TEXT_LENGTH:
        return None
    sentences = _sentences(cleaned, title=title)
    if len(sentences) < MIN_ARTICLE_SENTENCES:
        return None

    title_tokens = _tokens(title)
    ranked = sorted(
        enumerate(sentences),
        key=lambda item: (
            _sentence_score(item[1], item[0], title_tokens),
            -item[0],
        ),
        reverse=True,
    )
    selected: list[tuple[int, str]] = []
    for index, sentence in ranked:
        if _sentence_score(sentence, index, title_tokens) < 2:
            continue
        if selected and _too_similar(selected[0][1], sentence):
            continue
        expected = sum(len(value) for _, value in selected) + len(selected)
        expected += len(sentence)
        if expected > max_length:
            continue
        selected.append((index, sentence))
        if len(selected) == 2:
            break

    if not selected:
        return None
    return " ".join(value for _, value in sorted(selected)).strip()


def create_collected_summary(candidate: dict) -> str:
    """수집 시 원문 브리핑을 만들고 모든 실패를 RSS 설명으로 격리합니다."""
    title = str(candidate.get("title", "")).strip()
    fallback = create_brief(
        str(candidate.get("summary", "")).strip() or title,
        max_length=ARTICLE_SUMMARY_MAX_LENGTH,
    )
    if str(candidate.get("source", "")).strip() != "연합뉴스TV":
        return fallback

    try:
        html_text = fetch_article_html(str(candidate.get("url", "")))
        article_text = extract_article_text(html_text)
        brief = create_extractive_brief(article_text, title=title)
        return brief or fallback
    except Exception:
        return fallback
