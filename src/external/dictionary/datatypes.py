from datetime import datetime, timezone
import logging
from dataclasses import field
from pathlib import Path

from marshmallow_dataclass import dataclass

from utils.fs import data_dir


@dataclass
class Rule:
    id: int
    name: str
    descr: str
    image: str = ''

    def get_image_path(self) -> Path:
        return data_dir()/self.image


@dataclass
class Word:
    id: int
    type: str
    word: str
    translation: str
    examples: list[str]
    mark: str

    def __str__(self):
        return f'{self.word}[{self.id}]'


@dataclass
class Rules:
    rules: list[Rule]

    def info(self, indent=' ') -> str:
        return f'{indent}Size: {len(self.rules)}'



@dataclass
class Dictionary:
    created: datetime = datetime.now(tz=timezone.utc)
    words: list[Word] = field(default_factory=list)

    def validate(self):
        ids = {}
        for word in self.words:
            if word.id not in ids:
                ids[word.id] = []
            ids[word.id].append(word)

        for v in ids.values():
            if len(v) > 1:
                logging.warning(f'Duplicated ID {v}')

    def get_word_by_id(self, word_id: int) -> Word | None:
        for word in self.words:
            if word.id == word_id:
                return word

        return None

    def info(self, indent='') -> str:
        return f'{indent}Updated: {self.created.strftime("%m-%d-%Y, %H:%M:%S")},\n{indent}Size: {len(self.words)}'


@dataclass
class KnowledgeBase:
    rules: Rules
    dictionary: Dictionary

    def info(self, indent='') -> str:
        next_indent = indent + "  "
        return f'{indent}Dictionary:\n{self.dictionary.info(next_indent)}\n{indent}Rules:\n{self.rules.info(next_indent)}'

