from dataclasses import dataclass
from typing import List, Dict, NamedTuple, TypedDict, Union


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


@dataclass
class TwitterResource(Resource):
  image_urls: Union[List[str], None]
  image_captions: Union[List[str], None]


@dataclass
class ScrapboxResource(Resource):
  image_urls: Union[List[str], None]
  image_captions: Union[List[str], None]
