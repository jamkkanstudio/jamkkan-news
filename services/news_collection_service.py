import hashlib
import json
import os
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from uuid import UUID

from services.auth_service import require_automation_admin
from services.news_service import load_news, save_news, save_news_to_supabase
from services.rss_service import fetch_rss_news
from services.summarizer import create_brief, create_reason
from services.supabase_service import get_setting, upsert_setting
from services.time_service import KST


COLLECTION_STATUS_KEY = "news_collection_status"
COLLECTION_LOCK_FILE = Path(".news_collection.lock")
LOCK_STALE_SECONDS = 30 * 60
MAX_SEEN_FINGERPRINTS = 500
COLLECTION_STALE_AFTER = timedelta(minutes=30)
TRACKING_QUERY_KEYS = {
    "fbclid",
    "gclid",
    "utm_campaign",
    "utm_content",
    "utm_medium",
    "utm_source",
    "utm_term",
}


class CollectionError(RuntimeError):
    """안전한 오류 코드만 외부에 노출하는 수집 실패입니다."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class CollectionStatus:
    status: str
    last_attempt_at: str
    last_success_at: str | None
    added_count: int
    duplicate_count: int
    failure_code: str | None
    seen_fingerprints: list[str]


def canonicalize_url(url: str) -> str:
    """추적 쿼리와 조각을 제거해 중복 비교용 URL을 만듭니다."""
    parts = urlsplit(str(url).strip())
    query = urlencode(
        sorted(
            (key, value)
            for key, value in parse_qsl(parts.query, keep_blank_values=True)
            if key.lower() not in TRACKING_QUERY_KEYS
        )
    )
    return urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            parts.path.rstrip("/") or "/",
            query,
            "",
        )
    )


def article_id(source: str, source_id: str, url: str) -> str:
    """RSS 기사 ID를 우선 사용해 재실행에도 같은 UUID를 생성합니다."""
    identity = source_id.strip() or canonicalize_url(url)
    digest = hashlib.sha256(
        f"{source.strip().lower()}\0{identity}".encode("utf-8")
    ).digest()[:16]
    return str(UUID(bytes=digest, version=5))


def article_fingerprint(source: str, source_id: str, url: str) -> str:
    """삭제된 기사가 RSS에 남아 있어도 다시 등록하지 않도록 지문을 만듭니다."""
    identity = source_id.strip() or canonicalize_url(url)
    return hashlib.sha256(
        f"{source.strip().lower()}\0{identity}".encode("utf-8")
    ).hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _parse_collection_time(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def format_collection_time_kst(value: object) -> str:
    """수집 시각을 관리자에게 일관된 한국 시각으로 표시합니다."""
    parsed = _parse_collection_time(value)
    if parsed is None:
        return "확인 불가"
    return parsed.astimezone(KST).strftime("%Y-%m-%d %H:%M KST")


def is_collection_status_stale(
    status: dict,
    *,
    now: datetime | None = None,
) -> bool:
    """마지막 성공 후 30분 이상 지나면 운영 지연으로 봅니다."""
    last_success = _parse_collection_time(status.get("last_success_at"))
    if last_success is None:
        return True
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone.utc) - last_success.astimezone(
        timezone.utc
    ) >= COLLECTION_STALE_AFTER


def _build_news(candidate: dict) -> dict:
    category = candidate.get("category", "기타")
    if category == "최신":
        category = "기타"
    cleaned_summary = candidate.get("summary", "")
    return {
        "id": article_id(
            candidate.get("source", ""),
            candidate.get("source_id", ""),
            candidate.get("url", ""),
        ),
        "title": candidate.get("title", "").strip(),
        "summary": create_brief(
            cleaned_summary or candidate.get("title", "")
        ),
        "reason": create_reason(
            category=category,
            title=candidate.get("title", ""),
        ),
        "source": candidate.get("source", "").strip(),
        "url": candidate.get("url", "").strip(),
        "category": category,
        "importance": 50,
        "created_at": candidate.get("published_at") or _now_iso(),
    }


@contextmanager
def collection_lock(lock_file: Path = COLLECTION_LOCK_FILE):
    """한 작업 공간에서 수집 프로세스가 겹치지 않게 합니다."""
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(
            lock_file,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY,
        )
    except FileExistsError as error:
        age = datetime.now().timestamp() - lock_file.stat().st_mtime
        if age <= LOCK_STALE_SECONDS:
            raise CollectionError("collection_locked") from error
        lock_file.unlink(missing_ok=True)
        descriptor = os.open(
            lock_file,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY,
        )

    try:
        os.write(descriptor, b"locked\n")
        os.close(descriptor)
        yield
    finally:
        try:
            os.close(descriptor)
        except OSError:
            pass
        lock_file.unlink(missing_ok=True)


def _write_status(status: CollectionStatus) -> None:
    if not upsert_setting(COLLECTION_STATUS_KEY, asdict(status)):
        raise CollectionError("status_write_failed")


def load_collection_status() -> dict | None:
    """관리 화면에 표시할 마지막 자동 수집 상태를 읽습니다."""
    status = get_setting(COLLECTION_STATUS_KEY)
    if isinstance(status, str):
        try:
            status = json.loads(status)
        except json.JSONDecodeError:
            return None
    return status if isinstance(status, dict) else None


def collect_latest_news(
    *,
    feed_limit: int = 20,
    add_limit: int = 5,
    lock_file: Path = COLLECTION_LOCK_FILE,
) -> CollectionStatus:
    """최신 RSS를 중복 없이 JSON과 Supabase에 함께 저장합니다."""
    require_automation_admin()
    attempted_at = _now_iso()
    previous_status = load_collection_status() or {}
    last_success_at = previous_status.get("last_success_at")
    seen_fingerprints = list(
        dict.fromkeys(previous_status.get("seen_fingerprints", []))
    )[-MAX_SEEN_FINGERPRINTS:]
    seen_set = set(seen_fingerprints)

    with collection_lock(lock_file):
        try:
            candidates = fetch_rss_news(category="최신", limit=feed_limit)
        except Exception as error:
            failure = CollectionStatus(
                status="failed",
                last_attempt_at=attempted_at,
                last_success_at=last_success_at,
                added_count=0,
                duplicate_count=0,
                failure_code="rss_fetch_failed",
                seen_fingerprints=seen_fingerprints,
            )
            _write_status(failure)
            raise CollectionError("rss_fetch_failed") from error

        existing_news = load_news()
        existing_ids = {
            str(news.get("id", "")).strip()
            for news in existing_news
            if news.get("id")
        }
        existing_urls = {
            canonicalize_url(news.get("url", ""))
            for news in existing_news
            if news.get("url")
        }
        batch_ids = set()
        batch_urls = set()
        batch_fingerprints = set()
        additions = []
        pending_fingerprints = []
        duplicate_count = 0

        for candidate in candidates:
            if not candidate.get("title") or not candidate.get("url"):
                continue
            prepared = _build_news(candidate)
            prepared_url = canonicalize_url(prepared["url"])
            fingerprint = article_fingerprint(
                prepared["source"],
                candidate.get("source_id", ""),
                prepared["url"],
            )
            if (
                fingerprint in seen_set
                or prepared["id"] in existing_ids
                or prepared_url in existing_urls
            ):
                duplicate_count += 1
                if fingerprint not in seen_set:
                    seen_fingerprints.append(fingerprint)
                    seen_set.add(fingerprint)
                continue
            if (
                fingerprint in batch_fingerprints
                or prepared["id"] in batch_ids
                or prepared_url in batch_urls
            ):
                duplicate_count += 1
                continue
            additions.append(prepared)
            pending_fingerprints.append(fingerprint)
            batch_fingerprints.add(fingerprint)
            batch_ids.add(prepared["id"])
            batch_urls.add(prepared_url)
            if len(additions) >= add_limit:
                break

        for news in additions:
            if not save_news_to_supabase(news):
                failure = CollectionStatus(
                    status="failed",
                    last_attempt_at=attempted_at,
                    last_success_at=last_success_at,
                    added_count=0,
                    duplicate_count=duplicate_count,
                    failure_code="news_mirror_failed",
                    seen_fingerprints=seen_fingerprints[
                        -MAX_SEEN_FINGERPRINTS:
                    ],
                )
                _write_status(failure)
                raise CollectionError("news_mirror_failed")

        if additions:
            try:
                save_news(existing_news + additions)
            except OSError as error:
                failure = CollectionStatus(
                    status="failed",
                    last_attempt_at=attempted_at,
                    last_success_at=last_success_at,
                    added_count=0,
                    duplicate_count=duplicate_count,
                    failure_code="json_write_failed",
                    seen_fingerprints=seen_fingerprints[
                        -MAX_SEEN_FINGERPRINTS:
                    ],
                )
                _write_status(failure)
                raise CollectionError("json_write_failed") from error

        seen_fingerprints.extend(pending_fingerprints)

        success = CollectionStatus(
            status="success",
            last_attempt_at=attempted_at,
            last_success_at=attempted_at,
            added_count=len(additions),
            duplicate_count=duplicate_count,
            failure_code=None,
            seen_fingerprints=seen_fingerprints[-MAX_SEEN_FINGERPRINTS:],
        )
        _write_status(success)
        return success
