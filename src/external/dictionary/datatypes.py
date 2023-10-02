from datetime import datetime, timezone
import logging
from dataclasses import field
from marshmallow_dataclass import dataclass


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

    def info(self) -> str:
        return f'Updated: {self.created}, Size: {len(self.words)}'
