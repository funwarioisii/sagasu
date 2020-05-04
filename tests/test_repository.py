from sagasu.repository import SampleRepository

def test_load():
  repository = SampleRepository()
  resource = repository.load()
  assert resource.sentence == 'この1冊で合格！AWS認定　ソリューションアーキテクト・アソシエイト　テキスト&問題集\n'
