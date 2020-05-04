from dataclasses import dataclass
from typing import List, Dict, NamedTuple, TypedDict


@dataclass
class Resource:
  uri: str
  sentence: str

@dataclass
class TokenizedResource:
  index: List[str]
  resource: Resource

@dataclass
class IndexedResource(TypedDict):
  index: str
  resource: List[Resource]

@dataclass
class SampleResource(Resource):
  pass
