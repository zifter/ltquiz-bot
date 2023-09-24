import enum
from dataclasses import field
from marshmallow_dataclass import dataclass


@dataclass
class Word:
    type: str
    word: str
    translation: str
    examples: list[str]
    mark: str


@dataclass
class Dictionary:
    words: list[Word] = field(default_factory=list)
