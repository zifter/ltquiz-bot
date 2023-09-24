import pytest

from external.dictionary.datatypes import Dictionary, Word
from ltquiz.quiz import Quiz


def create_quiz(word: Word):
    return Quiz(Dictionary(
        words=[
            word,
        ]
    ))


@pytest.mark.parametrize("word,expected", (
        (
                Word(type='noun', word='test', translation='trans', examples=[], mark=''),
                '''
*test*

||trans||
'''
        ),
        (
            Word(type='noun', word='test', translation='trans', examples=['example'], mark='mark'),
            '''
*test*

example

||trans [mark]||
'''
        )
    ),
)
def test_quiz_template(word, expected):
    q = create_quiz(word)
    got = q.next_word()
    assert expected == got
