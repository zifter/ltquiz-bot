import dataclasses
import logging

from google.cloud.firestore import Client

from external.db.models import UserKnownWord
from external.dictionary.datatypes import Word

logger = logging.getLogger('storage')


class StorageFacade:
    def __init__(self, client: Client, namespace: str = ''):
        self.client = client
        self.namespace = namespace

    def collection_id(self, telegram_id):
        return f'{self.namespace}/{telegram_id}/known-words'

    def migrate(self):
        pass

    def make_known(self, telegram_id: int, word: Word):
        _, doc_ref = self.client.collection(self.collection_id(telegram_id)).add({'word': word.word})
        logger.debug(f'Added document with ID: {doc_ref.id}')

    def is_known(self, telegram_id: int, word: Word) -> bool:
        logger.info(f'Is known word? {telegram_id} {word}')

        known_word_ref = self.client.collection(self.collection_id(telegram_id))
        known_word_ref.where('word', '==', word.word)
        for word in known_word_ref.stream():
            return True

        return False
