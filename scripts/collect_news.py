import sys

from services.auth_service import AuthorizationError
from services.news_collection_service import CollectionError, collect_latest_news


def main() -> int:
    try:
        status = collect_latest_news()
    except AuthorizationError:
        print("news_collection status=failed code=authorization_failed")
        return 1
    except CollectionError as error:
        print(f"news_collection status=failed code={error.code}")
        return 1
    except Exception:
        print("news_collection status=failed code=internal_error")
        return 1

    print(
        "news_collection status=success "
        f"added={status.added_count} duplicates={status.duplicate_count}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
