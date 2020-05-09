from dataclasses import dataclass
from typing import List

import yaml

from sagasu import util


@dataclass
class SourceModel:
  source_type: str
  target: str


@dataclass
class ConfigModel:
  sources: List[SourceModel]


class Config:
  def __init__(self):
    self.path = f"{util.SAGASU_WORKDIR}/config/config.yml"

  def load(self) -> ConfigModel:
    with open(self.path) as f:
      _config = yaml.safe_load(f)
      config = ConfigModel(
        sources=[
          SourceModel(
            source_type=c['source_type'],
            target=c['target']
          )
          for c in _config['sources']
        ]
      )
    return config
