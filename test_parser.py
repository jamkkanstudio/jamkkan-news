from services.article_parser import parse_article


url = input("기사 URL을 입력하세요: ").strip()

try:
    article = parse_article(url)

    print("\n[제목]")
    print(article["title"])

    print("\n[언론사]")
    print(article["source"])

    print("\n[본문 일부]")
    print(article["content"][:1000])

except Exception as error:
    print(f"\n기사 가져오기 실패: {error}")