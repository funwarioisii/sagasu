import os
from pathlib import Path
from typing import List

import pandas as pd

from sagasu import model as m
from sagasu import util as u
from sagasu import crawler as c


class Repository:
  def load(self) -> List[m.Resource]:
    raise NotImplementedError("")


class SampleRepository(Repository):
  def __init__(self):
    u.mkdir_p((p := f'{u.SAGASU_WORKDIR}/sample/sample.txt'))
    with open(p, 'w') as f:
      f.write("""
吾輩は猫である。
親譲りの無鉄砲で小供の時から損ばかりしている。
""")

  def load(self) -> List[m.SampleResource]:
    with open(p := f'{u.SAGASU_WORKDIR}/sample/sample.txt') as f:
      document = f.readlines()
      document = ''.join(document)
    return [m.SampleResource(uri=p, sentence=document)]


class TwitterRepository(Repository):

  def load(self) -> List[m.TwitterResource]:
    dir_path = Path(f"{c.CRAWLER_WORK_DIR}/twitter/uri-sentence")
    uri_sentence_dfs = []
    for file in dir_path.iterdir():
      if not file.is_file():
        continue
      df = pd.read_csv(file, sep='\t')
      uri_sentence_dfs.append(df)
    uri_sentence_df = pd.concat(uri_sentence_dfs).reset_index()

    dir_path = Path(f"{c.CRAWLER_WORK_DIR}/twitter/uri-media")
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


class ScrapboxRepository(Repository):
  def load(self) -> List[m.ScrapboxResource]:
    dir_path = Path(f"{c.CRAWLER_WORK_DIR}/scrapbox/uri-sentence")
    uri_sentence_dfs = []
    for file in dir_path.iterdir():
      if not file.is_file():
        continue
      df = pd.read_csv(file, sep='\t')
      uri_sentence_dfs.append(df)
    uri_sentence_df = pd.concat(uri_sentence_dfs).reset_index()

    dir_path = Path(f"{c.CRAWLER_WORK_DIR}/scrapbox/uri-media")
    uri_media_dfs = []
    for file in dir_path.iterdir():
      if not file.is_file():
        continue
      df = pd.read_csv(file, sep='\t')
      uri_media_dfs.append(df)
    uri_media_df = pd.concat(uri_media_dfs).reset_index()

    df = pd.merge(uri_sentence_df, uri_media_df)
    # media_url1  media_url2  media_url3  media_url4  media_caption1
    resources = [m.ScrapboxResource(
      uri=r[1].uri, sentence=r[1].sentence,
      image_urls=[r[1].media_url1, r[1].media_url2, r[1].media_url3, r[1].media_url4],
      image_captions=[r[1].media_caption1, r[1].media_caption2, r[1].media_caption3, r[1].media_caption4]
    ) for r in df.iterrows()]

    return resources
