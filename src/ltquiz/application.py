import asyncio
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.constants import ParseMode

from external.api import ExternalAPI
from external.dictionary.datatypes import Dictionary, KnowledgeBase, Rule
from external.tg import Message, CallbackQuery, CallbackData
from ltquiz.quiz import Quiz

logger = logging.getLogger('app')


class BotApplication:
    def __init__(self, external: ExternalAPI, knowledge: KnowledgeBase, version: str):
        self.external = external
        self.knowledge: KnowledgeBase = knowledge
        self.quiz = Quiz(knowledge, external.db)
        self.version: str = version

        self.external.tg.add_message_processor(self.process_message)
        self.external.tg.add_callback_processor(self.process_callback)

    def run_polling(self):
        self.external.tg.run_polling()

    def run_webhook(self, *args):
        self.external.tg.run_webhook(*args)

    def migrate(self):
        self.external.db.migrate()

        commands = [
            BotCommand('/quiz_lt', 'Показывать слова на литовском и скрытый перевод'),
            BotCommand('/quiz_ru', 'Показывать слова на русском и скрытый перевод'),
            BotCommand('/rules', 'Показывать правила'),
            BotCommand('/info', 'Показать информацию о боте'),
        ]
        asyncio.run(self.external.tg.set_my_commands(commands))

    async def next_word(self, telegram_id, mode):
        word = self.quiz.next_word(telegram_id)
        text = self.quiz.template_word_card(word, mode)

        word_data = CallbackData('next', {'mode': mode})
        know_data = CallbackData('know', {'mode': mode, 'word_id': word.id})
        stop_data = CallbackData('stop', {})

        word = InlineKeyboardButton("next", callback_data=word_data.serialize())
        know = InlineKeyboardButton("know", callback_data=know_data.serialize())
        stop = InlineKeyboardButton("stop", callback_data=stop_data.serialize())
        reply_markup = InlineKeyboardMarkup([[word, know, stop]])

        await self.external.tg.send_message(telegram_id, text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

    async def next_rule(self, telegram_id):
        rule = self.quiz.next_rule(telegram_id)
        text = self.quiz.template_rule(rule)

        word_data = CallbackData('next_rule', {})
        stop_data = CallbackData('stop', {})

        word = InlineKeyboardButton("next", callback_data=word_data.serialize())
        stop = InlineKeyboardButton("stop", callback_data=stop_data.serialize())
        reply_markup = InlineKeyboardMarkup([[word, stop]])

        kwargs = {
            'parse_mode': ParseMode.HTML,
            'reply_markup': reply_markup,
        }
        if rule.image:
            await self.external.tg.send_photo(telegram_id, text, rule.get_image_path(), **kwargs)
        else:
            await self.external.tg.send_message(telegram_id, text, **kwargs)

    async def process_message(self, msg: Message):
        logger.info(f'Received: {msg}')

        if msg.text == '/quiz_lt':
            await self.next_word(msg.telegram_id, 'lt')
        if msg.text == '/quiz_ru':
            await self.next_word(msg.telegram_id, 'ru')
        if msg.text == '/rules':
            await self.next_rule(msg.telegram_id)
        elif msg.text == '/info':
            text = f'''
Version: {self.version},
Knowledge DB: 
{self.knowledge.info()}
            '''
            await self.external.tg.send_message(msg.telegram_id, text)
        else:
            logger.error('Unknown command')

    async def process_callback(self, callback: CallbackQuery):
        await self.external.tg.delete_message(callback.chat_id, callback.message_id)

        if callback.callback_data.name == 'next':
            await self.next_word(callback.telegram_id, callback.callback_data.data['mode'])
        if callback.callback_data.name == 'next_rule':
            await self.next_rule(callback.telegram_id)
        elif callback.callback_data.name == 'know':
            word_id = callback.callback_data.data['word_id']
            word = self.knowledge.dictionary.get_word_by_id(word_id)
            self.quiz.know_word(callback.telegram_id, word)
            await self.next_word(callback.telegram_id, callback.callback_data.data['mode'])
        elif callback.callback_data.name == 'stop':
            pass
        else:
            logger.error('Unknown callback')
