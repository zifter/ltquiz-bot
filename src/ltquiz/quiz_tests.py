from unittest.mock import MagicMock

import pytest

from external.dictionary.datatypes import Dictionary, Word
from external.storage import StorageFacade
from ltquiz.quiz import Quiz


def create_quiz(word: Word):
    words = [
        word,
    ]
    db = StorageFacade(None)
    d = Dictionary(words=words)

    return Quiz(d, db)


@pytest.mark.parametrize("word,expected", (
        (
                Word(id=1, type='noun', word='test', translation='trans', examples=[], mark=''),
                '''
<b>test</b>

<span class="tg-spoiler">trans</span>
'''
        ),
        (
            Word(id=1, type='noun', word='test', translation='trans', examples=['example'], mark='mark'),
            '''
<b>test</b>

example

<span class="tg-spoiler">trans [mark]</span>
'''
        )
    ),
)
def test_quiz_template(word, expected):
    q = create_quiz(word)
    text = q.template_card(word, 'lt')
    assert expected == text


def test_create_quiz():
    word = Word(id=1, type='noun', word='test', translation='trans', examples=[], mark='')
    q = create_quiz(word)
    q.db.is_known = MagicMock(return_value=False)
    q.next_word(1)
