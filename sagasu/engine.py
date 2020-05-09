from typing import List

from sagasu.indexer import WordNgramIndexer
from sagasu.repository import Repository, SampleRepository, TwitterRepository, ScrapboxRepository
from sagasu.model import Resource, IndexedResource
from sagasu.config import ConfigModel, SourceModel


class SearchEngine:
  def __init__(self, config: ConfigModel):
    self.indexers = [WordNgramIndexer(n=1), WordNgramIndexer(n=2), WordNgramIndexer(n=3)]
    self.indexed_resource = IndexedResource()
    self.config = config
    self.repositories: List[Repository] = \
        [self.load_repository(source) for source in self.config.sources]

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
