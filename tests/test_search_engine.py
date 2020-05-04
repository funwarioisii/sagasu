from sagasu.engine import SearchEngine

def test_indexing():
  engine = SearchEngine()
  engine.indexing()
  assert 'この' in engine.indexed_resource


def test_search():
  engine = SearchEngine()
  engine.indexing()
  assert 'AWS' in engine.word_search('AWS')[0].sentence
