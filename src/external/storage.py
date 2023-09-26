import logging

from google.cloud.ndb import Client

from external.db.models import UserKnownWord
from external.dictionary.datatypes import Word

logger = logging.getLogger('storage')


class StorageFacade:
    def __init__(self, client: Client):
        self.client = client

    def make_known(self, telegram_id: int, word: Word) -> UserKnownWord:
        word = UserKnownWord(
            telegram_id=telegram_id,
            word_id=word.id,
        )
        with self.client.context():
            word.put()

        return word

    def is_known(self, telegram_id: int, word: Word) -> bool:
        logger.info(f'Is known word? {telegram_id} {word}')

        with self.client.context():
            query = UserKnownWord.query_word(telegram_id, word.id)
            for app in query:
                return True

            return False
