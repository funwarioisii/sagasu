import datetime
import os
from pathlib import Path

SAGASU_WORKDIR = f"{os.getenv('HOME')}/.sagasu"
JST = datetime.timezone(datetime.timedelta(hours=+9), "JST")


def mkdir_p(file_path):
    (p := Path(file_path).parent).mkdir(parents=True, exist_ok=True)
    p.touch()


def is_exist(file_path):
    return Path(f"{SAGASU_WORKDIR}{file_path}").exists()
