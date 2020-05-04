import click
from sagasu.engine import SearchEngine

@click.command()
def app():
  word = input(">>> ")
  engine = SearchEngine()
  engine.indexing()
  resources = engine.word_search(word)
  for resource in resources:
    print(f"""
[URI]
  {resource.uri}
[Sentence]
  {resource.sentence[:30]}...
    """)


if __name__ == '__main__':
    app()