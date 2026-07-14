from services.rss_service import fetch_rss_news


try:
    news_list = fetch_rss_news(category="최신", limit=5)

    for index, news in enumerate(news_list, start=1):
        print(f"\n{index}. {news['title']}")
        print(news["url"])
        print(news["published_at"])

except Exception as error:
    print(f"RSS 가져오기 실패: {error}")