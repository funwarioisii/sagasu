from typing import List

from sagasu.indexer import WordNgramIndexer
from sagasu.repository import Repository, SampleRepository, TwitterRepository
from sagasu.model import Resource, IndexedResource


class SearchEngine:
  def __init__(self):
    self.repositories: List[Repository] = [SampleRepository(), TwitterRepository()]
    self.indexers = [WordNgramIndexer(n=1), WordNgramIndexer(n=2), WordNgramIndexer(n=3)]
    self.indexed_resource = IndexedResource()
  
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
