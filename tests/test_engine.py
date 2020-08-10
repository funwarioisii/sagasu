from sagasu.config import ConfigModel, SourceModel
from sagasu.engine import SearchEngine, CrawlerEngine

source = SourceModel(source_type='scrapbox', target='funwarioisii-test')
engine = CrawlerEngine([source])


def test_indexing():
  config = ConfigModel([
    SourceModel(source_type="dummy", target="dummy")
  ])
  search_engine = SearchEngine(config)
  search_engine.indexing()


def test_crawl_all():
  engine.crawl_all()
  assert 'Scrapbox' in engine.resources[0].sentence
  assert engine.resources[0].uri.startswith('https://scrapbox.io/funwarioisii-test')
