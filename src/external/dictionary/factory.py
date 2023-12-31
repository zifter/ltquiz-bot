import csv
from datetime import datetime, timezone
from io import StringIO

import requests

from external.dictionary.datatypes import Dictionary, Word, KnowledgeBase, Rules
from utils import fs
from utils.fs import DICT_PATH, RULES_PATH

# URL = 'https://docs.google.com/spreadsheets/d/1QSg0_z6ffrrqre8YLIdu83kWCSKzfZcYJIVeUzJ9o4g/edit?hl=ru#gid=0'
URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTQeF0VmI5PxHDpwKGrIR7VQ8b439DwWvb0nTtDfCWA8hlNcHICbVGMjLweirf5DXAniuA_8Tu2kOav/pub?gid=0&single=true&output=csv'


def get_stable_id(v: str):
    n = int.from_bytes(v.encode(), 'little')
    return n % (2 ** 32 - 1)


class KnowledgeBaseFactory:
    @staticmethod
    def create_knowledge_base() -> KnowledgeBase:
        return KnowledgeBase(
            rules=KnowledgeBaseFactory.load_rules_from_file(),
            dictionary=KnowledgeBaseFactory.load_dictionary_from_file(),
        )

    @staticmethod
    def load_dictionary_from_file(filepath=DICT_PATH) -> Dictionary:
        with open(filepath, 'r', encoding='utf-8') as f:
            s = f.read()

        return KnowledgeBaseFactory.load_dictionary_from_json_string(s)

    @staticmethod
    def load_dictionary_from_json_string(s) -> Dictionary:
        d = Dictionary.Schema().loads(s)
        return d

    @staticmethod
    def load_rules_from_file(filepath=RULES_PATH) -> Rules:
        with open(filepath, 'r', encoding='utf-8') as f:
            s = f.read()

        d = Rules.Schema().loads(s)
        return d

    @staticmethod
    def generate_dicitionary_from_google_sheet(data_dir=fs.data_dir(), url=URL):
        response = requests.get(url)
        response.encoding = 'utf-8'
        if response.status_code != 200:
            raise RuntimeError(f'Status is not 200 {response.status_code}')

        csv_data = StringIO(response.text)
        reader = csv.reader(csv_data)

        d = Dictionary(
            created=datetime.now(tz=timezone.utc)
        )
        # Process the CSV data, e.g., iterate through rows and columns
        for row in reader:
            if not row[1]:
                continue

            # Process each column
            word = Word(
                id=get_stable_id(row[0] + row[1]),
                type=row[0],
                word=row[1],
                translation=row[2],
                examples=[v for v in row[3].split('\n') if v],
                mark=row[4]
            )
            d.words.append(word)

        d.words = sorted(d.words[1:], key=lambda w: w.word)

        d.validate()

        with open(data_dir / 'dict.json', 'w', encoding='utf8') as f:
            value = Dictionary.Schema().dumps(d, indent=2, ensure_ascii=False)
            f.write(value)

        return d
