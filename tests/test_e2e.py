"""In this file, we will not use assert sentence. only check normally process will done w/o errors."""

from sagasu.config import ConfigModel, SourceModel
from sagasu.engine import SearchEngine, CrawlerEngine


def test_indexing():
    config = ConfigModel([
        SourceModel(source_type="dummy", target="dummy")
    ])
    search_engine = SearchEngine(config)
    crawler_engine = CrawlerEngine(config.sources)
    crawler_engine.crawl_all()
    search_engine.indexing()
    search_engine.indexed_resource.dump()


def test_reduce_indexing_stream():
    config = ConfigModel([
        SourceModel(source_type="dummy", target="dummy"),
        SourceModel(source_type="dummy", target="dummy"),
        SourceModel(source_type="dummy", target="dummy"),
    ])
    search_engine = SearchEngine(config)
    search_engine.reduce_indexing_stream()
    search_engine.indexed_resource.dump()


def test_search():
    config = ConfigModel([
        SourceModel(source_type="dummy", target="dummy")
    ])
    search_engine = SearchEngine(config)
    print(type(search_engine.indexed_resource.indexed))
    print(search_engine.indexed_resource.indexed['dummy'])
    result = search_engine.word_search('dummy')
    print(result)
