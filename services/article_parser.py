from urllib.parse import urlparse

import trafilatura
from newspaper import Article


def get_source_name(url: str) -> str:
    """URL의 도메인으로 임시 언론사 이름을 만듭니다."""
    domain = urlparse(url).netloc.lower()

    domain = domain.replace("www.", "")
    domain = domain.replace("n.news.", "")
    domain = domain.replace("news.", "")

    return domain.split(".")[0]


def parse_with_trafilatura(url: str) -> dict:
    """trafilatura를 사용해 기사 정보를 추출합니다."""
    downloaded = trafilatura.fetch_url(url)

    if not downloaded:
        raise ValueError("기사 페이지를 불러오지 못했습니다.")

    metadata = trafilatura.extract_metadata(downloaded)

    text = trafilatura.extract(
        downloaded,
        include_comments=False,
        include_tables=False,
        favor_precision=True,
    )

    if not text:
        raise ValueError("기사 본문을 찾지 못했습니다.")

    title = metadata.title if metadata and metadata.title else ""
    source = metadata.sitename if metadata and metadata.sitename else ""

    return {
        "title": title.strip(),
        "content": text.strip(),
        "source": source.strip(),
        "url": url,
    }


def parse_with_newspaper(url: str) -> dict:
    """newspaper4k를 사용해 기사 정보를 추출합니다."""
    article = Article(url, language="ko")
    article.download()
    article.parse()

    if not article.text:
        raise ValueError("기사 본문을 찾지 못했습니다.")

    source = get_source_name(url)

    return {
        "title": article.title.strip(),
        "content": article.text.strip(),
        "source": source,
        "url": url,
    }


def parse_article(url: str) -> dict:
    """
    기사 URL에서 제목, 본문, 언론사를 추출합니다.

    1차로 trafilatura를 사용하고,
    실패하면 newspaper4k를 사용합니다.
    """
    if not url.startswith(("http://", "https://")):
        raise ValueError("URL은 http:// 또는 https://로 시작해야 합니다.")

    try:
        result = parse_with_trafilatura(url)
    except Exception:
        result = parse_with_newspaper(url)

    if not result["title"]:
        result["title"] = "제목을 가져오지 못했습니다."

    if not result["source"]:
        result["source"] = get_source_name(url)

    return result