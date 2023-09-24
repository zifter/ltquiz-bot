import asyncio
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, BotCommand

from external.api import ExternalAPI
from external.dictionary.datatypes import Dictionary
from external.tg import Message, CallbackQuery, CallbackData
from ltquiz.quiz import Quiz

logger = logging.getLogger('app')


class BotApplication:
    def __init__(self, external: ExternalAPI, d: Dictionary):
        self.external = external
        self.quiz = Quiz(d)

        self.external.tg.add_message_processor(self.process_message)
        self.external.tg.add_callback_processor(self.process_callback)

    def run_polling(self):
        self.external.tg.run_polling()

    def run_webhook(self, *args):
        self.external.tg.run_webhook(*args)

    def migrate(self):
        commands = [
            BotCommand('/next', 'Next word'),
            BotCommand('/info', 'Info about this bot'),
        ]
        asyncio.run(self.external.tg.set_my_commands(commands))

    async def next_word(self, chat_id):
        text = self.quiz.next_word()

        know_data = CallbackData('know', {})
        repeat_data = CallbackData('repeat', {})

        next = InlineKeyboardButton("next", callback_data=repeat_data.serialize())
        know = InlineKeyboardButton("know", callback_data=know_data.serialize())
        reply_markup = InlineKeyboardMarkup([[next, know]])

        await self.external.tg.send_message(chat_id, text, parse_mode='MarkdownV2', reply_markup=reply_markup)

    async def process_message(self, msg: Message):
        logger.info(f'Received: {msg}')

        if msg.text == '/next':
            await self.next_word(msg.telegram_id)

    async def process_callback(self, callback: CallbackQuery):
        await self.external.tg.delete_message(callback.chat_id, callback.message_id)

        await self.next_word(callback.telegram_id)
