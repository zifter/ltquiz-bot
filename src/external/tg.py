import asyncio
import logging
from enum import Enum
from pathlib import Path

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, Application, MessageHandler, filters, CallbackQueryHandler
from telegram.helpers import escape_markdown

logger = logging.getLogger('telegram')


import dataclasses
import json
from dataclasses import dataclass


@dataclass
class CallbackData:
    name: str
    data: dict

    def serialize(self) -> str:
        return json.dumps(dataclasses.asdict(self))

    @staticmethod
    def deserialize(data) -> 'CallbackData':
        return CallbackData(**json.loads(data))


class MessageContentType(Enum):
    NONE = 0
    COMMAND = 1
    TEXT = 2
    VOICE = 3


class Message:
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.update = update
        self.context = context

    @property
    def text(self) -> str:
        return self.update.message.text


    @property
    def message_id(self) -> int:
        return self.update.message.id

    @property
    def telegram_id(self):
        return self.update.message.from_user.id


class CallbackQuery:
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.update = update
        self.context = context

    @property
    def callback_data(self) -> CallbackData:
        return CallbackData.deserialize(self.update.callback_query.data)

    @property
    def telegram_id(self):
        return self.update.callback_query.from_user.id

    @property
    def chat_id(self) -> int:
        return self.update.effective_message.chat_id

    @property
    def message_id(self) -> int:
        return self.update.effective_message.id

class TelegramFacade:
    def __init__(self, token):
        self._message_processors: list = []
        self._callback_processors: list = []

        self.application: Application = Application.builder().token(token).build()

        self.application.add_handler(MessageHandler(filters.TEXT, self.receive_message))
        self.application.add_handler(CallbackQueryHandler(self.receive_callback))

    def add_message_processor(self, message_processor):
        self._message_processors.append(message_processor)

    def add_callback_processor(self, process_callback):
        self._callback_processors.append(process_callback)

    async def receive_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info(f'Message {update.message}')

        for processor in self._message_processors:
            await processor(Message(update, context))

    async def receive_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info(f'Callback {update.message}')

        for callback in self._callback_processors:
            await callback(CallbackQuery(update, context))

    async def delete_message(self, chat_id: int, message_id: int):
        logger.info(f'Delete message {chat_id}')

        await self.application.bot.delete_message(chat_id=chat_id, message_id=message_id)

    async def send_message(self, chat_id: int, text: str, **kwargs):
        logger.info(f'Send message {chat_id} {text}')
        await self.application.bot.send_message(chat_id=chat_id, text=text, **kwargs)

    async def send_photo(self, chat_id: int, text: str, filename: Path, **kwargs):
        logger.info(f'Send message {chat_id} {text}')
        await self.application.bot.send_photo(chat_id=chat_id, photo=filename, caption=text, **kwargs)

    async def set_my_commands(self, commands):
        await self.application.bot.set_my_commands(commands)

    def run_polling(self):
        self.application.run_polling()

    def run_webhook(self, port, secret_token, url):
        self.application.run_webhook(
            listen="0.0.0.0",
            port=port,
            secret_token=secret_token,
            webhook_url=url
        )
