import asyncio
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, BotCommand

from external.api import ExternalAPI
from external.dictionary.datatypes import Dictionary
from external.tg import Message, CallbackQuery, CallbackData
from ltquiz.quiz import Quiz

logger = logging.getLogger('app')


class BotApplication:
    def __init__(self, external: ExternalAPI, d: Dictionary, version: str):
        self.external = external
        self.d: Dictionary = d
        self.quiz = Quiz(d, external.db)
        self.version: str = version

        self.external.tg.add_message_processor(self.process_message)
        self.external.tg.add_callback_processor(self.process_callback)

    def run_polling(self):
        self.external.tg.run_polling()

    def run_webhook(self, *args):
        self.external.tg.run_webhook(*args)

    def migrate(self):
        commands = [
            BotCommand('/word', 'Show word card'),
            BotCommand('/info', 'Info about this bot'),
        ]
        asyncio.run(self.external.tg.set_my_commands(commands))

    async def next_word(self, telegram_id):
        word, text = self.quiz.next_word(telegram_id)

        word_data = CallbackData('next', {})
        know_data = CallbackData('know', {'word_id': word.id})

        word = InlineKeyboardButton("next", callback_data=word_data.serialize())
        know = InlineKeyboardButton("know", callback_data=know_data.serialize())
        reply_markup = InlineKeyboardMarkup([[word, know]])

        await self.external.tg.send_message(telegram_id, text, parse_mode='MarkdownV2', reply_markup=reply_markup)

    async def process_message(self, msg: Message):
        logger.info(f'Received: {msg}')

        if msg.text == '/word':
            await self.next_word(msg.telegram_id)
        elif msg.text == '/info':
            text = f'''
Version: {self.version},
Dictionary: 
{self.d.info()}
            '''
            await self.external.tg.send_message(msg.telegram_id, text)
        else:
            logger.error('Unknown command')

    async def process_callback(self, callback: CallbackQuery):
        await self.external.tg.delete_message(callback.chat_id, callback.message_id)

        if callback.callback_data.name == 'next':
            await self.next_word(callback.telegram_id)
        elif callback.callback_data.name == 'know':
            word_id = callback.callback_data.data['word_id']
            word = self.d.get_word_by_id(word_id)
            self.quiz.know(callback.telegram_id, word)
        else:
            logger.error('Unknown callback')
