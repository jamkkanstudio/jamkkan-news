from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


KST = ZoneInfo("Asia/Seoul")


def now_kst() -> datetime:
    """현재 시각을 명시적인 한국 표준시로 반환합니다."""
    return datetime.now(KST)


def today_kst() -> date:
    """현재 날짜를 한국 표준시 기준으로 반환합니다."""
    return now_kst().date()


def current_week_dates() -> list[date]:
    """KST 기준 이번 주 월요일부터 일요일까지 반환합니다."""
    today = today_kst()
    monday = today - timedelta(days=today.weekday())
    return [monday + timedelta(days=offset) for offset in range(7)]


def datetime_to_kst_date(value: datetime) -> date:
    """시각을 KST 날짜로 변환합니다. 과거의 naive 값은 KST로 해석합니다."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=KST)
    else:
        value = value.astimezone(KST)
    return value.date()
