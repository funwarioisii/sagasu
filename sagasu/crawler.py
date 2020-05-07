import datetime
import os
from typing import List

import pandas as pd
import tweepy
from sagasu.model import Resource, TwitterResource
from sagasu import util

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')


class Crawler:
  def __init__(self, path_prefix: str):
    self.path_prefix = path_prefix
    self.resources: List[Resource] = []

  def _collect(self) -> List[Resource]:
    raise NotImplementedError("not implemented")

  def _dump(self):
    raise NotImplementedError("not implemented")

  def __call__(self, *args, **kwargs):
    self.resources = self._collect()
    self._dump()


class CrawlerEngine:
  def __init__(self):
    self.crawlers: List[Crawler] = self.register()
    self.resources = []

  def register(self) -> List[Crawler]:
    return [
      TwitterFavoriteCrawler()
    ]

  def crawl_all(self):
    for crawler in self.crawlers:
      crawler()
      self.resources += crawler.resources


class TwitterFavoriteCrawler(Crawler):
  def __init__(self, path_prefix: str = f"{os.getenv('HOME')}/.sagasu"):
    super().__init__(path_prefix)
    self.resources: List[TwitterResource] = []

  def _collect(self) -> List[Resource]:
    statuses: List[tweepy.models.Status] = self._load_favorites()

    resources = []
    for status in statuses:
      uri = f"https://twitter.com/_/status/{status.id}"
      sentence = ''.join(status.text.split("\n"))
      media_urls = []
      media_captions = []

      if 'media' in status.entities:
        for media in status.extended_entities['media']:
          media_url = media['media_url']
          media_caption = self._image_captioning(media_url)
          media_urls.append(media_url)
          media_captions.append(media_caption)

      resources.append(TwitterResource(
        uri=uri,
        sentence=sentence,
        image_urls=media_urls,
        image_captions=media_captions
      ))

    return resources

  def _image_captioning(self, media_url: str) -> str:
    if not ((e := 'SAGASU_IMAGE_CAPTIONING') in os.environ and os.environ[e]):
      return "empty"
    else:
      raise NotImplementedError("not implemented")

  def _load_favorites(self) -> List[tweepy.models.Status]:
    statuses = []
    for n in range(10):
      statuses += api.favorites('funwarioisii', page=n+1)
    return statuses

  def _dump(self):
    t = datetime.datetime.now(JST)
    filename_prefix = f"/{t.year}-" \
                      f"{m if len(m := str(t.month)) == 2 else f'0{m}'}-" \
                      f"{d if len(d := str(t.day)) == 2 else f'0{d}'}-" \
                      f"{h if len(h := str(t.hour)) == 2 else f'{h}'}"
    resource_type_prefix = "/uri-sentence"

    filename = self.path_prefix + resource_type_prefix + filename_prefix + ".tsv"
    util.mkdir_p(filename)

    uri_sentence_pairs = list(map(lambda resource: [resource.uri, resource.sentence], self.resources))
    pd.DataFrame(uri_sentence_pairs, columns=["uri", "sentence"]).to_csv(filename, sep="\t")

    resource_type_prefix = "/media-sentence"
    filename = self.path_prefix + resource_type_prefix + filename_prefix + ".tsv"
    util.mkdir_p(filename)

    def extract(resource: List[str]):
      _1, _2, _3, _4 = (resource + ["empty", "empty", "empty", "empty"])[:4]
      return _1, _2, _3, _4

    uri_media_pairs = list(
      map(
        lambda resource: [resource.uri] + list(extract(resource.image_urls)) + list(extract(resource.image_captions)),
        self.resources))
    pd.DataFrame(
      uri_media_pairs,
      columns=[
        "uri",
        "media_url1", "media_url2", "media_url3", "media_url4",
        "media_caption1", "media_caption2", "media_caption3", "media_caption4"]) \
      .to_csv(filename, sep="\t")
    return
