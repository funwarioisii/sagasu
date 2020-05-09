import click

from sagasu.engine import SearchEngine
from sagasu.crawler import CrawlerEngine
from sagasu.config import Config
from sagasu import util as u


@click.command()
@click.argument('mode')
def app(mode):
  if mode not in ["search", "crawl", "indexing"]:
    print("choice in [search, crawl, indexing]")
    return

  if not u.is_exist("/config/config.yml"):
    print("please set ~/.sagasu/config/config.yml")
    return

  config = Config().load()
  engine = SearchEngine(config)

  if mode == "crawl":
    crawler_engine = CrawlerEngine(config.sources)
    crawler_engine.crawl_all()
  elif mode == "indexing":
    engine.indexing()
  elif mode == "search":
    word = input("let's type search word >>> ")
    resources = engine.word_search(word)
    for resource in resources:
      print(f"""
  [URI]
    {resource.uri}
  [Sentence]
    {resource.sentence[:30]}...
      """)


if __name__ == '__main__':
  app()
