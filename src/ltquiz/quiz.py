import dataclasses
import random
from copy import deepcopy
from typing import Tuple

import jinja2
from telegram.helpers import escape_markdown

from external.dictionary.datatypes import Dictionary, Word
from external.storage import StorageFacade

_TEMPLATE = '''
<b>{{word}}</b>

{%- if examples %}

{{ examples|random }}
{%- endif %}

<span class="tg-spoiler">{{ translation }}{%- if mark %} [{{ mark }}]{% endif %}</span>

'''


class Quiz:
    def __init__(self, d: Dictionary, db: StorageFacade):
        self.dictionary = d
        self.db = db

        env = jinja2.Environment()
        self.template = env.from_string(_TEMPLATE)

    def next_word(self, telegram_id: int) -> tuple[Word, str]:
        attempts = 5
        word = random.choice(self.dictionary.words)
        while attempts > 0:
            if not self.db.is_known(telegram_id, word):
                break

            attempts -= 1
            word = random.choice(self.dictionary.words)

        return word, self.template.render(dataclasses.asdict(word))


    def know(self, telegram_id: int, word: Word):
        self.db.make_known(telegram_id, word)
