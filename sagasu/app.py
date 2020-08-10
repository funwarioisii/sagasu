import click

from sagasu import util as u
from sagasu.config import ConfigUtil
from sagasu.engine import SearchEngine


@click.command()
@click.argument("mode")
def app(mode):
    if mode not in ["search", "indexing", "async"]:
        print("choice in [search, crawl, indexing]")
        return

    if not u.is_exist("/config/config.yml"):
        print("please set ~/.sagasu/config/config.yml")
        return

    config = ConfigUtil().load()
    print("start setup Search Engine")
    search_engine = SearchEngine(config)
    print("done setup Search Engine")

    if mode == "indexing":
        # crawler_engine = CrawlerEngine(config.sources)
        # crawler_engine.crawl_all()
        search_engine.reduce_indexing_stream()
        # search_engine.indexed_resource.dump()
    elif mode == "search":
        word = input("let's type search word >>> ")
        resources = search_engine.word_search(word)
        if not resources:
            print(f"unknown word")
            print(f"{search_engine.indexed_resource.indexed.keys()}")
        resources = set(resources)
        for resource in resources:
            print(f"""
[URI]
  {resource.uri}
[Sentence]
  {resource.sentence[:30]}...
""")


if __name__ == "__main__":
    app()
