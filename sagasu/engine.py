from typing import List

from sagasu.indexer import WordUnigramIndexer
from sagasu.repository import Repository, SampleRepository
from sagasu.model import Resource, IndexedResource


class SearchEngine:
  def __init__(self):
    self.repositories: List[Repository] = [SampleRepository]
    self.indexer = WordUnigramIndexer()
    self.indexed_resource = IndexedResource()
  
  def _load_all(self) -> List[Resource]:
    resources = []
    for RepositoryType in self.repositories:
      repository = RepositoryType()
      resources.append(repository.load())
    return resources

  def indexing(self):
    resources = self._load_all()
    for resource in resources:
      self.indexed_resource = self.indexer(resource, self.indexed_resource)
    return

  def word_search(self, word: str) -> List[Resource]:
    if {} == self.indexed_resource:
      raise Exception("run indexing before call searching")
    return self.indexed_resource[word]
