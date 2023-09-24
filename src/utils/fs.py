import sys
from os import getcwd, path, pardir
from pathlib import Path


def working_dir() -> Path:
    return Path(getcwd())


def repo_dir() -> Path:
    return Path(path.abspath(path.join(__file__, pardir, pardir, pardir)))


def data_dir() -> Path:
    return repo_dir() / 'data'


DICT_PATH = data_dir() / 'dict.json'
