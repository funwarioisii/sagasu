import os
from pathlib import Path
from typing import List

import pandas as pd

from sagasu import model as m


class Repository:
  def load(self) -> List[m.Resource]:
    raise NotImplementedError("")


class SampleRepository(Repository):
  def load(self) -> List[m.SampleResource]:
    with open('data/sample/sample.txt') as f:
      document = f.readlines()
      document = ''.join(document)
    return [m.SampleResource(uri='data/sample/sample.txt', sentence=document)]


class TwitterRepository(Repository):

  def load(self) -> List[m.TwitterResource]:
    dir_path = Path(f"{os.getenv('HOME')}/.sagasu/uri-sentence")
    uri_sentence_dfs = []
    for file in dir_path.iterdir():
      if not file.is_file():
        continue
      df = pd.read_csv(file, sep='\t')
      uri_sentence_dfs.append(df)
    uri_sentence_df = pd.concat(uri_sentence_dfs).reset_index()

    dir_path = Path(f"{os.getenv('HOME')}/.sagasu/uri-media")
    uri_media_dfs = []
    for file in dir_path.iterdir():
      if not file.is_file():
        continue
      df = pd.read_csv(file, sep='\t')
      uri_media_dfs.append(df)
    uri_media_df = pd.concat(uri_media_dfs).reset_index()

    df = pd.merge(uri_sentence_df, uri_media_df)
    # media_url1  media_url2  media_url3  media_url4  media_caption1
    resources = [m.TwitterResource(
      uri=r[1].uri, sentence=r[1].sentence,
      image_urls=[r[1].media_url1, r[1].media_url2, r[1].media_url3, r[1].media_url4],
      image_captions=[r[1].media_caption1, r[1].media_caption2, r[1].media_caption3, r[1].media_caption4]
    ) for r in df.iterrows()]

    return resources
