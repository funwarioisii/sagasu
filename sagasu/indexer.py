import datetime
import pickle
from typing import List

import spacy

from sagasu.model import Resource, IndexedResource
from sagasu.util import mkdir_p, SAGASU_WORKDIR, JST

nlp = spacy.load("ja_ginza")


def word_n_gram(sentence: str, n: int = 1) -> List[str]:
    doc = nlp(sentence)
    tokens = []
    for sent in doc.sents:
        for token in sent:
            tokens.append(token.orth_)
    index = ["".join(tokens[idx: idx + n]) for idx in range(len(tokens) - n + 1)]
    return index


def dump(func):
    def runner(*args, **kwargs):
        result = func(*args, **kwargs)
        mkdir_p(file_path := f"{SAGASU_WORKDIR}/indexed/{datetime.datetime.now(JST).strftime('%Y-%m-%d-%H')}.pkl")
        with open(file_path, "wb") as f:
            pickle.dump(result, f)
        return result

    return runner


class Indexer:
    def __call__(self, resource: Resource, indexed: IndexedResource) -> IndexedResource:
        raise NotImplementedError("not implemented")


class WordNgramIndexer(Indexer):
    def __init__(self, n):
        self.n = n

    def __call__(self, resource: Resource, indexed: IndexedResource) -> IndexedResource:
        indices = word_n_gram(resource.sentence, self.n)
        for index in indices:
            if index not in indexed.indexed:
                indexed.indexed[index] = [resource]
            else:
                indexed.indexed[index].append(resource)
        return indexed


if __name__ == "__main__":
    r = Resource(uri="1", sentence="毎日の料理を楽しみにする")
    indexed_resource = IndexedResource(indexed={})
    print(WordNgramIndexer(2)(r, indexed_resource))
    print(WordNgramIndexer(3)(r, indexed_resource))
