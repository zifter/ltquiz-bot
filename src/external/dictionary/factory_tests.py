import json

from external.dictionary.factory import KnowledgeBaseFactory
from utils.fs import DICT_PATH


def test_create_knowledge_base():
    k = KnowledgeBaseFactory.create_knowledge_base()
    assert k

    for rule in k.rules.rules:
        if rule.image:
            assert rule.get_image_path().exists()


def test_load_dictionary_from_file():
    d = KnowledgeBaseFactory.load_dictionary_from_file()
    assert d.words


def test_load_rules_from_file():
    d = KnowledgeBaseFactory.load_rules_from_file()
    assert d.rules


def test_factory_load_string():
    assert KnowledgeBaseFactory.load_dictionary_from_json_string('{}')


def test_factory_generate():
    assert KnowledgeBaseFactory.generate_dicitionary_from_google_sheet()
