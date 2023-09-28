import dataclasses
import random
from copy import deepcopy
from typing import Tuple

import jinja2
from telegram.helpers import escape_markdown

from external.dictionary.datatypes import Dictionary, Word
from external.storage import StorageFacade

_TEMPLATE_ORIG = '''
<b>{{word}}</b>

{%- if examples %}

{{ examples|random }}
{%- endif %}

<span class="tg-spoiler">{{ translation }}{%- if mark %} [{{ mark }}]{% endif %}</span>

'''

_TEMPLATE_TRAN = '''
<b>{{translation}}</b>

{%- if examples %}

{{ examples|random }}
{%- endif %}

<span class="tg-spoiler">{{ word }}{%- if mark %} [{{ mark }}]{% endif %}</span>

'''


class Quiz:
    def __init__(self, d: Dictionary, db: StorageFacade):
        self.dictionary = d
        self.db = db

        env = jinja2.Environment()
        self._template_orig = env.from_string(_TEMPLATE_ORIG)
        self._template_tran = env.from_string(_TEMPLATE_TRAN)

    def next_word(self, telegram_id: int) -> Word:
        attempts = 5
        word = random.choice(self.dictionary.words)
        while attempts > 0:
            if not self.db.is_known(telegram_id, word):
                break

            attempts -= 1
            word = random.choice(self.dictionary.words)

        return word

    def template_card(self, word: Word, mode: str) -> str:
        if mode == 'lt':
            return self._template_orig.render(dataclasses.asdict(word))
        else:
            return self._template_tran.render(dataclasses.asdict(word))

    def know(self, telegram_id: int, word: Word):
        self.db.make_known(telegram_id, word)
