from typing import List
import os
import pickle

import spacy
import datetime

from sagasu.model import Resource, IndexedResource
from sagasu.util import mkdir_p

nlp = spacy.load('ja_ginza')
JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')


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


def dump(func):
  def runner(*args, **kwargs):
    result = func(*args, **kwargs)
    t = datetime.datetime.now(JST)
    path_prefix = f"{os.getenv('HOME')}/.sagasu"
    filename_prefix = f"/{t.year}-" \
                      f"{m if len(m := str(t.month)) == 2 else f'0{m}'}-" \
                      f"{d if len(d := str(t.day)) == 2 else f'0{d}'}-" \
                      f"{h if len(h := str(t.hour)) == 2 else f'{h}'}"

    mkdir_p(file_path := path_prefix + "/indexed" + filename_prefix + ".pkl")
    with open(file_path, 'wb') as f:
      pickle.dump(result, f)
    return result

  return runner


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


class WordNgramIndexer(Indexer):
  def __init__(self, n):
    self.n = n

  @dump
  def __call__(self, resource: Resource, indexed: IndexedResource) -> IndexedResource:
    indices = word_n_gram(resource.sentence, self.n)
    for index in indices:
      if index not in indexed:
        indexed[index] = [resource]
      else:
        indexed[index].append(resource)
    return indexed


if __name__ == '__main__':
  print(simple_n_gram('毎日の料理を楽しみにする', 2))
  print(word_n_gram('毎日の料理を楽しみにする'))
  print(word_n_gram('毎日の料理を楽しみにする', 2))
