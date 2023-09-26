from google.cloud import ndb


class UserKnownWord(ndb.Model):
    telegram_id = ndb.IntegerProperty()
    word_id = ndb.IntegerProperty()

    @classmethod
    def query_word(cls, telegram_id: int, word_id: int):
        return cls.query(cls.telegram_id == telegram_id, cls.word_id == word_id)

    def __str__(self):
        return f'User{self.telegram_id}'
