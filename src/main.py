import logging
import os
import sys

from argparse import ArgumentParser

from google.cloud import ndb

from external.api import ExternalAPI
from external.dictionary.factory import DictionaryFactory
from external.tg import TelegramFacade

from ltquiz.application import BotApplication
from external.storage import StorageFacade


logger = logging.getLogger('lt-quiz-bot')


logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def env_var(env, default=None, prefix='LT_QUIZ_'):
    return os.environ.get(f'{prefix}{env}', default)


def get_args():
    parser = ArgumentParser()
    parser.add_argument("--environment-name", default=env_var('ENVIRONMENT_NAME', 'test'), type=str)
    parser.add_argument("--telegram-token", default=env_var('TELEGRAM_TOKEN', None))

    subparsers = parser.add_subparsers(dest='command')

    parser_handler = subparsers.add_parser('polling', help='Run Telegram MessageHandler')
    parser_handler.set_defaults(command_func=cmd_polling)

    parser_handler = subparsers.add_parser('webhook', help='Run Telegram MessageHandler')
    parser_handler.add_argument("--secret-token", default=env_var('SECRET_TOKEN', None), type=str)
    parser_handler.add_argument("--url", default=env_var('URL', None), type=str)
    parser_handler.add_argument("--port", default=int(env_var('PORT', 8080)), type=int)
    parser_handler.set_defaults(command_func=cmd_webhook)

    parser_init = subparsers.add_parser('generate', help='Generate DB')
    parser_init.set_defaults(command_func=cmd_generate)

    return parser.parse_args()


def cmd_polling(app: BotApplication):
    app.run_polling()


def cmd_webhook(app: BotApplication, port: int, secret_token: str, url: str):
    app.run_webhook(port, secret_token, url)


def cmd_generate(app: BotApplication):
    DictionaryFactory.generate_from_google_sheet()


def main(command_func,
         command: str,
         environment_name: str,
         telegram_token: str,
         **kwargs):
    logger.info(f'Start bot with command {command}')

    external = ExternalAPI(
        db=StorageFacade(ndb.Client(namespace=environment_name)),
        tg=TelegramFacade(telegram_token),
    )
    d = DictionaryFactory.load_json_file()
    bot = BotApplication(external, d)
    command_func(bot, **kwargs)


if __name__ == '__main__':
    args = get_args()
    logger.info(args)

    main(**vars(args))
