import datetime
import json
from dataclasses import dataclass, asdict
from typing import List, Union, Dict

from sagasu.util import SAGASU_WORKDIR, mkdir_p

JST = datetime.timezone(datetime.timedelta(hours=+9), "JST")


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
class IndexedResource:
    indexed: Dict[str, List[Resource]]

    def dump(self):
        mkdir_p(file_path := f"{SAGASU_WORKDIR}/indexed/{datetime.datetime.now(JST).strftime('%Y-%m-%d-%H')}.json")
        with open(file_path, "w") as f:
            f.write(json.dumps(asdict(self)))


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


@dataclass
class DummyResource(Resource):
    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return super().__eq__(other)
