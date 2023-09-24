from google.cloud.ndb import Client


class StorageFacade:
    def __init__(self, client: Client):
        self.client = client
