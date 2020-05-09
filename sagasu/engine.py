import pickle
from functools import reduce
from pathlib import Path
from typing import List

from sagasu.config import ConfigModel, SourceModel
from sagasu.indexer import WordNgramIndexer
from sagasu.model import Resource, IndexedResource
from sagasu.repository import Repository, TwitterRepository, ScrapboxRepository
from sagasu.util import SAGASU_WORKDIR


class SearchEngine:
  def __init__(self, config: ConfigModel):
    self.indexers = [WordNgramIndexer(n=1), WordNgramIndexer(n=2), WordNgramIndexer(n=3)]
    self.indexed_resource = self.load_indexed() if Path(f"{SAGASU_WORKDIR}/indexed") else IndexedResource()
    self.config = config
    self.repositories: List[Repository] = \
      [self.load_repository(source) for source in self.config.sources]

  def load_indexed(self):
    p = reduce(
      lambda pre, cur: max(pre, cur, key=lambda f: f.stat().st_ctime),
      [p for p in Path(f"{SAGASU_WORKDIR}/indexed").iterdir()]
    )
    p.absolute()
    with p.open('rb') as f:
      indexed = pickle.load(f)
    return indexed

  @staticmethod
  def load_repository(source: SourceModel) -> Repository:
    if source.source_type == "twitter":
      return TwitterRepository()
    elif source.source_type == "scrapbox":
      return ScrapboxRepository()

  def _load_all(self) -> List[Resource]:
    resources = []
    for repository in self.repositories:
      _resources = repository.load()
      resources += _resources
    return resources

  def indexing(self):
    resources = self._load_all()
    for resource in resources:
      for indexer in self.indexers:
        self.indexed_resource = indexer(resource, self.indexed_resource)
    return

  def word_search(self, word: str) -> List[Resource]:
    if {} == self.indexed_resource:
      raise Exception("run indexing before call searching")
    elif word not in self.indexed_resource:
      return []
    return self.indexed_resource[word]
