import requests
from django.conf import settings


class ClientApi:
    def get_data(self, title):
        data = requests.get(self.create_url(title))

        return data.json()

    @staticmethod
    def create_url(title):
        return '{}{}&t={}'.format(settings.REMOTE_API_URL, settings.REMOTE_API_KEY, title)
