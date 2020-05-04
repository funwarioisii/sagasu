from sagasu.model import Resource, SampleResource


class Repository:
  def load(self) -> Resource:
    raise NotImplementedError("")



class SampleRepository(Repository):
  def load(self)  -> SampleResource:
    with open('data/sample/sample.txt') as f:
      document = f.readlines()
      document = ''.join(document)
    return SampleResource(uri='data/sample/sample.txt', sentence=document)
