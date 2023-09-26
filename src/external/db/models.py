from dataclasses import dataclass


@dataclass
class UserKnownWord:
    telegram_id: int
    word_id: int

    def __str__(self):
        return f'User{self.telegram_id}'
