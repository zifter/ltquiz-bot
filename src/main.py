import logging
import os
import sys

from argparse import ArgumentParser
from pathlib import Path
from typing import Callable

from google.cloud import firestore

from external.api import ExternalAPI
from external.dictionary.factory import KnowledgeBaseFactory
from external.tg import TelegramFacade

from ltquiz.application import BotApplication
from external.storage import StorageFacade
from utils import fs

logger = logging.getLogger('lt-quiz-bot')


logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def env_var(env, default=None, prefix='LT_QUIZ_'):
    return os.environ.get(f'{prefix}{env}', default)


def get_args():
    parser = ArgumentParser()
    parser.add_argument("--gcp-project-id", default=env_var('GCP_PROJECT_ID', 'test'), type=str)
    parser.add_argument("--environment-name", default=env_var('ENVIRONMENT_NAME', 'test'), type=str)
    parser.add_argument("--version", default=env_var('VERSION', 'local'), type=str)
    parser.add_argument("--telegram-token", default=env_var('TELEGRAM_TOKEN', None))

    subparsers = parser.add_subparsers(dest='command')

    parser_polling = subparsers.add_parser('polling', help='Run Telegram MessageHandler')
    parser_polling.set_defaults(command_func=cmd_polling)

    parser_webhook = subparsers.add_parser('webhook', help='Run Telegram MessageHandler')
    parser_webhook.add_argument("--secret-token", default=env_var('SECRET_TOKEN', None), type=str)
    parser_webhook.add_argument("--url", default=env_var('URL', None), type=str)
    parser_webhook.add_argument("--port", default=int(env_var('PORT', 8080)), type=int)
    parser_webhook.set_defaults(command_func=cmd_webhook)

    parser_gen = subparsers.add_parser('generate', help='Generate dictionary')
    parser_gen.add_argument("--data-dir", default=env_var('DATA_DIR', fs.data_dir()), type=Path)
    parser_gen.set_defaults(command_func=cmd_generate)

    parser_migrate = subparsers.add_parser('migrate', help='Migrate App')
    parser_migrate.set_defaults(command_func=cmd_migrate)

    return parser.parse_args()


def create_bot(gcp_project_id: str, environment_name: str, telegram_token: str, version: str):
    external = ExternalAPI(
        db=StorageFacade(firestore.Client(project=gcp_project_id), namespace=environment_name),
        tg=TelegramFacade(telegram_token),
    )
    knowledge = KnowledgeBaseFactory.create_knowledge_base()
    return BotApplication(external, knowledge, version)


def cmd_polling(bot_creator: Callable[[], BotApplication]):
    bot_creator().run_polling()


def cmd_webhook(bot_creator: Callable[[], BotApplication], port: int, secret_token: str, url: str):
    bot_creator().run_webhook(port, secret_token, url)


def cmd_generate(bot_creator: Callable[[], BotApplication], data_dir):
    KnowledgeBaseFactory.generate_dicitionary_from_google_sheet(data_dir)


def cmd_migrate(bot_creator: Callable[[], BotApplication]):
    bot_creator().migrate()


def main(command_func,
         command: str,
         gcp_project_id: str,
         environment_name: str,
         telegram_token: str,
         version: str,
         **kwargs):
    logger.info(f'Start bot with command {command}')

    def bot_creator() -> BotApplication:
        return create_bot(gcp_project_id, environment_name, telegram_token, version)

    command_func(bot_creator, **kwargs)


if __name__ == '__main__':
    args = get_args()
    logger.info(args)

    main(**vars(args))
