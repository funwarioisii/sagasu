import datetime
import json
import os
import re
from functools import reduce
from time import sleep
from typing import List

import pandas as pd
import requests as req
import tweepy
from tqdm import tqdm

from sagasu import model as m
from sagasu import util
from sagasu.config import SourceModel
from sagasu.model import DummyResource

if os.getenv('SAGASU_CAPTION'):
    from sagasu.image_captioning import image_captioning_from_url

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

CRAWLER_WORK_DIR = util.SAGASU_WORKDIR + "/crawler"

JST = datetime.timezone(datetime.timedelta(hours=+9), "JST")


class Crawler:
    def __init__(self, source: SourceModel):
        self.path_prefix = CRAWLER_WORK_DIR
        self.resources: List[m.Resource] = []
        self.source = source

    def _collect(self) -> List[m.Resource]:
        raise NotImplementedError("not implemented")

    def _dump(self):
        raise NotImplementedError("not implemented")

    def __call__(self, *args, **kwargs):
        self.resources = self._collect()
        self._dump()

    @staticmethod
    def _image_captioning(media_url: str) -> str:
        return image_captioning_from_url(media_url)


class DummyCrawler(Crawler):
    def _collect(self) -> List[m.Resource]:
        return [
            DummyResource(uri="dummy", sentence="ある晴れた日のこと。魔法以上の愉快が限りなく降り注ぐ不可能じゃないわ。")
        ]

    def _dump(self):
        pass


class TwitterFavoriteCrawler(Crawler):
    def __init__(self, source: SourceModel):
        super().__init__(source)
        self.path_prefix += "/twitter"
        self.resources: List[m.TwitterResource] = []

    def _collect(self) -> List[m.Resource]:
        statuses: List[tweepy.models.Status] = self._load_favorites()

        resources = []
        for status in statuses:
            uri = f"https://twitter.com/_/status/{status.id}"
            sentence = "".join(status.text.split("\n"))
            media_urls = []
            media_captions = []

            if "media" in status.entities:
                for media in status.extended_entities["media"]:
                    media_url = media["media_url"]
                    media_caption = (
                        self._image_captioning(media_url)
                        if os.getenv("SAGASU_CAPTION")
                        else "empty"
                    )
                    media_urls.append(media_url)
                    media_captions.append(media_caption)

            resources.append(
                m.TwitterResource(
                    uri=uri,
                    sentence=sentence,
                    image_urls=media_urls,
                    image_captions=media_captions,
                )
            )

        return resources

    def _load_favorites(self) -> List[tweepy.models.Status]:
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)

        statuses = []
        progress_bar = tqdm(total=10)
        progress_bar.set_description("collecting favorites")
        for n in range(10):
            statuses += api.favorites(self.source.target, page=n + 1)
            progress_bar.update(1)

        return statuses

    def _dump(self):
        filename_prefix = datetime.datetime.now(JST).strftime("/%Y-%m-%d-%H")
        resource_type_prefix = "/uri-sentence"

        filename = self.path_prefix + resource_type_prefix + filename_prefix + ".tsv"
        util.mkdir_p(filename)

        uri_sentence_pairs = list(
            map(lambda resource: [resource.uri, resource.sentence], self.resources)
        )
        pd.DataFrame(uri_sentence_pairs, columns=["uri", "sentence"]).to_csv(
            filename, sep="\t"
        )

        resource_type_prefix = "/uri-media"
        filename = self.path_prefix + resource_type_prefix + filename_prefix + ".tsv"
        util.mkdir_p(filename)

        def extract(resource: List[str]):
            _1, _2, _3, _4 = (resource + ["empty", "empty", "empty", "empty"])[:4]
            return _1, _2, _3, _4

        uri_media_pairs = list(
            map(
                lambda resource: [resource.uri]
                + list(extract(resource.image_urls))
                + list(extract(resource.image_captions)),
                self.resources,
            )
        )
        pd.DataFrame(
            uri_media_pairs,
            columns=[
                "uri",
                "media_url1",
                "media_url2",
                "media_url3",
                "media_url4",
                "media_caption1",
                "media_caption2",
                "media_caption3",
                "media_caption4",
            ],
        ).to_csv(filename, sep="\t")
        return


class ScrapboxCrawler(Crawler):
    def __init__(self, source: SourceModel):
        super().__init__(source=source)
        self.path_prefix += "/scrapbox"
        self.target = self.source.target

    def _collect(self) -> List[m.ScrapboxResource]:
        skip = 0
        limit = 100
        page_url = f"https://scrapbox.io/api/pages/{self.target}"

        responses = [req.get(f"{page_url}?skip={skip}&limit={limit}")]
        count = json.loads(responses[0].text)['count']
        skip += limit
        while count > skip:
            responses.append(req.get(f"{page_url}?skip={skip}&limit={limit}"))
            skip += limit

        resources = []
        pages = reduce(lambda x, y: x + y, [json.loads(res.text)['pages'] for res in responses])
        progress_bar = tqdm(total=len(pages))
        progress_bar.set_description("collecting scrapbox")
        for page in pages:
            title = t if "/" not in (t := page["title"]) else t.replace("/", "%2F")
            page = json.loads(req.get(f"{page_url}/{title}").text)
            sentence = " ".join(lines := list(
                map(lambda p: p.get("text"), page.get("lines") if page.get("lines") is not None else [])))
            image_uris = [s[1:-1] for s in lines if re.match(r"\[https://gyazo.com", s)]
            image_captions = ["empty" for _ in image_uris]
            resources.append(
                m.ScrapboxResource(
                    uri=f"https://scrapbox.io/{self.target}/{title}",
                    sentence=sentence,
                    image_urls=image_uris,
                    image_captions=image_captions,
                )
            )
            sleep(0.5)
            progress_bar.update(1)
        return resources

    def _dump(self):
        filename_prefix = datetime.datetime.now(JST).strftime("/%Y-%m-%d-%H")
        resource_type_prefix = "/uri-sentence"

        filename = self.path_prefix + resource_type_prefix + filename_prefix + ".tsv"
        util.mkdir_p(filename)
        uri_sentence_pairs = list(
            map(lambda resource: [resource.uri, resource.sentence], self.resources)
        )
        pd.DataFrame(uri_sentence_pairs, columns=["uri", "sentence"]).to_csv(
            filename, sep="\t"
        )

        resource_type_prefix = "/uri-media"
        filename = self.path_prefix + resource_type_prefix + filename_prefix + ".tsv"
        util.mkdir_p(filename)

        def extract(resource: List[str]):
            _1, _2, _3, _4 = (resource + ["empty", "empty", "empty", "empty"])[:4]
            return _1, _2, _3, _4

        uri_media_pairs = list(
            map(
                lambda resource: [resource.uri]
                + list(extract(resource.image_urls))
                + list(extract(resource.image_captions)),
                self.resources,
            )
        )
        pd.DataFrame(
            uri_media_pairs,
            columns=[
                "uri",
                "media_url1",
                "media_url2",
                "media_url3",
                "media_url4",
                "media_caption1",
                "media_caption2",
                "media_caption3",
                "media_caption4",
            ],
        ).to_csv(filename, sep="\t")
        return
