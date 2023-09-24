import csv
import dataclasses
import json
from io import StringIO

import requests

from external.dictionary.dictionary_types import Dictionary, Word
from utils.fs import DICT_PATH

# URL = 'https://docs.google.com/spreadsheets/d/1QSg0_z6ffrrqre8YLIdu83kWCSKzfZcYJIVeUzJ9o4g/edit?hl=ru#gid=0'
URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTQeF0VmI5PxHDpwKGrIR7VQ8b439DwWvb0nTtDfCWA8hlNcHICbVGMjLweirf5DXAniuA_8Tu2kOav/pub?gid=0&single=true&output=csv'


class DictionaryFactory:

    @staticmethod
    def load_json_file(filepath=DICT_PATH) -> Dictionary:
        with open(filepath, 'r', encoding='utf-8') as f:
            s = f.read()

        return DictionaryFactory.load_json_string(s)

    @staticmethod
    def load_json_string(s) -> Dictionary:
        d = Dictionary.Schema().loads(s)
        return d

    @staticmethod
    def generate_from_google_sheet(url=URL, target=DICT_PATH):
        response = requests.get(url)
        response.encoding = 'utf-8'
        if response.status_code != 200:
            raise RuntimeError(f'Status is not 200 {response.status_code}')

        csv_data = StringIO(response.text)
        reader = csv.reader(csv_data)

        d = Dictionary()
        # Process the CSV data, e.g., iterate through rows and columns
        for row in reader:
            # Process each column
            word = Word(
                type=row[0],
                word=row[1],
                translation=row[2],
                examples=[v for v in row[3].split('\n') if v],
                mark=row[4]
            )
            d.words.append(word)

        d.words = d.words[1:]

        with open(target, 'w', encoding='utf8') as f:
            value = Dictionary.Schema().dumps(d, indent=2, ensure_ascii=False)
            f.write(value)

        return d
