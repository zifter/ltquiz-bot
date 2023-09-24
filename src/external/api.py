from external.storage import StorageFacade
from external.tg import TelegramFacade


class ExternalAPI:
    def __init__(self, db: StorageFacade, tg: TelegramFacade):
        self.db = db
        self.tg = tg
