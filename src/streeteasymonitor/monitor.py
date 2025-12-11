import requests

from src.streeteasymonitor.search import Search
from src.streeteasymonitor.database import Database
from src.streeteasymonitor.email_notifier import EmailNotifier
from src.streeteasymonitor.config import Config


class Monitor:
    def __init__(self, **kwargs):
        self.config = Config()
        self.db = Database()

        self.session = requests.Session()
        self.session.headers.update(self.config.get_headers())

        self.kwargs = kwargs

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.session.close()

    def run(self):
        """Fetch new listings and return them. Caller handles email/DB insertion."""
        self.search = Search(self)
        self.listings = self.search.fetch()
        return self.listings
