import html
import re


CATEGORY_REASONS = {
    "경제": "금리·환율·증시 등 개인의 자산과 생활비에 영향을 줄 수 있습니다.",
    "정치": "정부 정책과 제도 변화가 국민 생활에 영향을 줄 수 있습니다.",
    "사회": "많은 사람의 안전과 일상생활에 관련된 소식입니다.",
    "국제": "해외 정세 변화가 국내 경제와 외교 환경에 영향을 줄 수 있습니다.",
    "테크": "기술 변화가 산업과 일자리, 일상생활을 바꿀 수 있습니다.",
    "AI": "AI 기술의 발전이 산업과 업무 방식에 영향을 줄 수 있습니다.",
    "기타": "오늘의 주요 흐름을 이해하는 데 필요한 소식입니다.",
}


def clean_text(text: str) -> str:
    """HTML 태그와 불필요한 공백을 제거합니다."""
    if not text:
        return ""

    cleaned = re.sub(r"<[^>]+>", " ", text)
    cleaned = html.unescape(cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip()


def create_brief(text: str, max_length: int = 140) -> str:
    """RSS 설명문을 최대 두 문장의 짧은 브리핑으로 정리합니다."""
    cleaned = clean_text(text)

    if not cleaned:
        return "기사 내용을 확인해 주세요."

    sentences = re.split(r"(?<=[.!?。])\s+", cleaned)
    selected_sentences = []
    current_length = 0

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        expected_length = current_length + len(sentence)

        if selected_sentences and expected_length > max_length:
            break

        selected_sentences.append(sentence)
        current_length = expected_length

        if len(selected_sentences) == 2:
            break

    brief = " ".join(selected_sentences).strip()

    if not brief:
        brief = cleaned[:max_length].strip()

    if len(brief) > max_length:
        brief = brief[:max_length].rstrip() + "…"

    return brief


def create_reason(category: str, title: str = "") -> str:
    """카테고리를 기준으로 중요한 이유를 생성합니다."""
    normalized_category = category if category in CATEGORY_REASONS else "기타"
    base_reason = CATEGORY_REASONS[normalized_category]

    title_lower = title.lower()

    if any(keyword in title_lower for keyword in ["금리", "한국은행"]):
        return "금리 변화는 대출 이자와 부동산·주식시장에 직접적인 영향을 줄 수 있습니다."

    if any(keyword in title_lower for keyword in ["환율", "달러"]):
        return "환율 변화는 수입 물가와 해외 투자, 기업 실적에 영향을 줄 수 있습니다."

    if any(keyword in title_lower for keyword in ["코스피", "코스닥", "증시"]):
        return "국내 증시 흐름은 투자심리와 기업 자금 조달 환경을 보여주는 지표입니다."

    if any(keyword in title_lower for keyword in ["ai", "인공지능"]):
        return "AI 기술 변화는 산업 경쟁력과 일하는 방식에 영향을 줄 수 있습니다."

    return base_reason