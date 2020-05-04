from typing import List

import spacy

from sagasu.model import Resource, IndexedResource

nlp = spacy.load('ja_ginza')


def simple_n_gram(sentence: str, n: int) -> List[str]:
  index = [sentence[idx:idx + n] for idx in range(len(sentence) - n + 1)]
  return index

def word_n_gram(sentence: str, n: int = 1) -> List[str]:
  doc = nlp(sentence)
  tokens = []
  for sent in doc.sents:
    for token in sent:
      tokens.append(token.orth_)
  index = [''.join(tokens[idx:idx + n]) for idx in range(len(tokens) - n + 1)]
  return index

class Indexer:
  def __call__(self, resource: Resource, indexed: IndexedResource) -> IndexedResource:
    raise NotImplementedError("not implemented")


class WordUnigramIndexer(Indexer):
  def __call__(self, resource: Resource, indexed: IndexedResource) -> IndexedResource:
    indices = word_n_gram(resource.sentence)
    for index in indices:
      if index not in indexed:
        indexed[index] = [resource]
      else:
        indexed[index].append(resource)
    return indexed


if __name__=='__main__':
    print(simple_n_gram('毎日の料理を楽しみにする', 2))
    print(word_n_gram('毎日の料理を楽しみにする'))
    print(word_n_gram('毎日の料理を楽しみにする', 2))
