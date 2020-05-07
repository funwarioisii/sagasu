import click
from sagasu.engine import SearchEngine
from sagasu.crawler import CrawlerEngine

@click.command()
@click.argument('mode')
def app(mode):
  if mode not in ["search", "crawl", "indexing"]:
    print("choice in [search, crawl, indexing]")
    return

  engine = SearchEngine()

  if mode == "indexing":
    engine.indexing()
  elif mode == "search":
    word = input("let's type search word >>> ")
    engine.indexing()
    resources = engine.word_search(word)
    for resource in resources:
      print(f"""
  [URI]
    {resource.uri}
  [Sentence]
    {resource.sentence[:30]}...
      """)
  elif mode == "crawl":
    crawler_engine = CrawlerEngine()
    crawler_engine.crawl_all()


if __name__ == '__main__':
  app()
