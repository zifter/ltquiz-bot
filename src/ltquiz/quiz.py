import dataclasses
import random

import jinja2

from external.dictionary.dictionary_types import Dictionary

_TEMPLATE = '''
*{{word}}*
{%- if examples %}
{{ examples|random }}
{% else %}

{%- endif %}
||{{ translation }}||
'''


class Quiz:
    def __init__(self, d: Dictionary):
        self.dictionary = d

        env = jinja2.Environment()
        self.template = env.from_string(_TEMPLATE)

    def next_word(self) -> str:
        word = random.choice(self.dictionary.words)
        return self.template.render(**dataclasses.asdict(word))
