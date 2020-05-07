from pathlib import Path


# "/1/2/3/4"
def mkdir_p(file_path):
  (p := Path(file_path).parent).mkdir(parents=True, exist_ok=True)
  p.touch()
