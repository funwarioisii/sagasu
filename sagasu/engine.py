import asyncio
import datetime
import pickle
from functools import reduce
from itertools import product
from pathlib import Path
from typing import List

from joblib import delayed, Parallel

from sagasu.config import ConfigModel, SourceModel
from sagasu.crawler import Crawler, TwitterFavoriteCrawler, ScrapboxCrawler, DummyCrawler
from sagasu.indexer import Indexer, WordNgramIndexer
from sagasu.model import Resource, IndexedResource
from sagasu.repository import Repository, TwitterRepository, ScrapboxRepository, DummyRepository
from sagasu.util import SAGASU_WORKDIR, mkdir_p, JST


class SearchEngine:
    def __init__(self, config: ConfigModel):
        self.indexers = [
            WordNgramIndexer(n=1),
            WordNgramIndexer(n=2),
            WordNgramIndexer(n=3),
        ]
        self.indexed_resource: IndexedResource = (
            self.load_indexed()
            if Path(f"{SAGASU_WORKDIR}/indexed").exists()
            else IndexedResource(indexed={})
        )
        self.config = config
        self.repositories: List[Repository] = [
            self.load_repository(source) for source in self.config.sources
        ]

    @staticmethod
    def load_indexed() -> IndexedResource:
        """return latest indexed resource"""
        p = reduce(
            lambda pre, cur: max(pre, cur, key=lambda f: f.stat().st_ctime),
            [p for p in Path(f"{SAGASU_WORKDIR}/indexed").iterdir() if p.suffix == '.pkl'],
        )

        indexed_resource = pickle.load(p.absolute().open('rb'))
        return indexed_resource

    @staticmethod
    def load_repository(source: SourceModel) -> Repository:
        if source.source_type == "twitter":
            return TwitterRepository()
        elif source.source_type == "scrapbox":
            return ScrapboxRepository()
        elif source.source_type == "dummy":
            return DummyRepository()

    def _load_all(self) -> List[Resource]:
        resources = []
        for repository in self.repositories:
            _resources = repository.load()
            resources += _resources
        return resources

    # experimental, will merge this into indexing
    def reduce_indexing_stream(self, dump=True):
        def _reduce_indexed_resources(r1: IndexedResource, r2: IndexedResource) -> IndexedResource:
            for r in r1.indexed:
                if r in r2.indexed:
                    r2.indexed[r] += r1.indexed[r]
                else:
                    r2.indexed[r] = r1.indexed[r]
            return r2

        async def run_stream(_loop: asyncio.AbstractEventLoop, crawlers: List[Crawler]) -> List[IndexedResource]:
            async def _run_indexing_stream(crawler: Crawler):
                return await _loop.run_in_executor(None, self.indexing_stream, crawler)
            return await asyncio.gather(*[_run_indexing_stream(crawler) for crawler in crawlers])

        loop = asyncio.get_event_loop()
        crawler_engine = CrawlerEngine(self.config.sources)
        indexed_resources = loop.run_until_complete(run_stream(loop, crawler_engine.crawlers))
        indexed_resource = reduce(_reduce_indexed_resources, indexed_resources)
        self.indexed_resource = indexed_resource

        if dump:
            mkdir_p(file_path := f"{SAGASU_WORKDIR}/indexed/{datetime.datetime.now(JST).strftime('%Y-%m-%d-%H')}.pkl")
            with open(file_path, "wb") as f:
                pickle.dump(indexed_resource, f)

    def indexing_stream(self, crawler: Crawler) -> IndexedResource:
        def _indexing(_indexer: Indexer, _resource: Resource) -> IndexedResource:
            return _indexer(_resource, IndexedResource(indexed={}))

        def _reduce_indexed_resources(r1: IndexedResource, r2: IndexedResource) -> IndexedResource:
            for r in r1.indexed:
                if r in r2.indexed:
                    r2.indexed[r] += r1.indexed[r]
                else:
                    r2.indexed[r] = r1.indexed[r]
            return r2

        crawler()
        resource_indexer_pairs = product(self.indexers, crawler.resources)
        print(f"start indexing: {crawler.source.source_type}")
        jobs = [delayed(_indexing)(*resource_indexer_pair) for resource_indexer_pair in resource_indexer_pairs]
        indexed_resources = Parallel(n_jobs=2)(jobs)
        indexed_resource = reduce(_reduce_indexed_resources, indexed_resources)
        print(f"done indexing: {crawler.source.source_type}")
        return indexed_resource

    def indexing(self, dump=True):
        def _indexing(_indexer: Indexer, _resource: Resource) -> IndexedResource:
            return _indexer(_resource, IndexedResource(indexed={}))

        def _reduce_indexed_resources(r1: IndexedResource, r2: IndexedResource) -> IndexedResource:
            for r in r1.indexed:
                if r in r2.indexed:
                    r2.indexed[r] += r1.indexed[r]
                else:
                    r2.indexed[r] = r1.indexed[r]
            return r2

        resources = self._load_all()
        resource_indexer_pairs = product(self.indexers, resources)
        jobs = [delayed(_indexing)(*resource_indexer_pair) for resource_indexer_pair in resource_indexer_pairs]
        indexed_resources = Parallel(n_jobs=4)(jobs)
        indexed_resource = reduce(_reduce_indexed_resources, indexed_resources)
        self.indexed_resource = indexed_resource
        if dump:
            mkdir_p(file_path := f"{SAGASU_WORKDIR}/indexed/{datetime.datetime.now(JST).strftime('%Y-%m-%d-%H')}.pkl")
            with open(file_path, "wb") as f:
                pickle.dump(indexed_resource, f)
        return

    def word_search(self, word: str) -> List[Resource]:
        if {} == self.indexed_resource:
            raise Exception("run indexing before call searching")
        elif word not in self.indexed_resource.indexed:
            return []
        return self.indexed_resource.indexed[word]


class CrawlerEngine:
    def __init__(self, sources: List[SourceModel]):
        self.resources = []
        self.crawlers: List[Crawler] = [self._load_crawler(source) for source in sources]

    def _load_crawler(self, source: SourceModel):
        if source.source_type == "twitter":
            return TwitterFavoriteCrawler(source)
        elif source.source_type == "scrapbox":
            return ScrapboxCrawler(source)
        elif source.source_type == "dummy":
            return DummyCrawler(source)

    def crawl_all(self):
        for crawler in self.crawlers:
            crawler()
            self.resources += crawler.resources
