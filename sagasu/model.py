from dataclasses import dataclass
from typing import List, TypedDict, Union


@dataclass
class Resource:
    uri: str
    sentence: str

    def __eq__(self, other):
        if type(other) is not Resource:
            return False
        elif other.uri == self.uri:
            return True
        else:
            return False

    def __hash__(self):
        return hash(self.uri)


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

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return super().__eq__(other)


@dataclass
class ScrapboxResource(Resource):
    image_urls: Union[List[str], None]
    image_captions: Union[List[str], None]

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return super().__eq__(other)


@dataclass
class SlackResource(Resource):
    pass
