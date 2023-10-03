import dataclasses
import random
from copy import deepcopy
from typing import Tuple

import jinja2
from telegram.helpers import escape_markdown

from external.dictionary.datatypes import Dictionary, Word, KnowledgeBase, Rule
from external.storage import StorageFacade

_TEMPLATE_WORD_ORIG = '''
<b>{{word}}</b>

{%- if examples %}

{{ examples|random }}
{%- endif %}

<span class="tg-spoiler">{{ translation }}{%- if mark %} [{{ mark }}]{% endif %}</span>

'''

_TEMPLATE_WORD_TRANS = '''
<b>{{translation}}</b>

{%- if examples %}

{{ examples|random }}
{%- endif %}

<span class="tg-spoiler">{{ word }}{%- if mark %} [{{ mark }}]{% endif %}</span>

'''

_TEMPLATE_RULE = '''
<b>{{name}}</b>

{%- if descr %}
{{ descr }}
{%- endif %}
'''



class Quiz:
    def __init__(self, knowledge: KnowledgeBase, db: StorageFacade):
        self.knowledge = knowledge
        self.db = db

        env = jinja2.Environment()
        self._template_word_orig = env.from_string(_TEMPLATE_WORD_ORIG)
        self._template_word_trans = env.from_string(_TEMPLATE_WORD_TRANS)
        self._template_rule = env.from_string(_TEMPLATE_RULE)

    def next_word(self, telegram_id: int) -> Word:
        attempts = 5
        word = random.choice(self.knowledge.dictionary.words)
        while attempts > 0:
            if not self.db.is_known(telegram_id, word):
                break

            attempts -= 1
            word = random.choice(self.knowledge.dictionary.words)

        return word

    def template_word_card(self, word: Word, mode: str) -> str:
        if mode == 'lt':
            return self._template_word_orig.render(dataclasses.asdict(word))
        else:
            return self._template_word_trans.render(dataclasses.asdict(word))

    def template_rule(self, rule: Rule) -> str:
        return self._template_rule.render(dataclasses.asdict(rule))

    def know_word(self, telegram_id: int, word: Word):
        self.db.make_known(telegram_id, word)

    def next_rule(self, telegram_id: int) -> Rule:
        rule = random.choice(self.knowledge.rules.rules)
        return rule
