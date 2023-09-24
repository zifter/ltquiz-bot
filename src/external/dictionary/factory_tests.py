import json

from external.dictionary.factory import DictionaryFactory
from utils.fs import DICT_PATH


def test_factory_load_file():
    d = DictionaryFactory.load_json_file(DICT_PATH)
    assert d.words


def test_factory_load_string():
    assert DictionaryFactory.load_json_string('{}')


def test_factory_generate():
    assert DictionaryFactory.generate_from_google_sheet()
