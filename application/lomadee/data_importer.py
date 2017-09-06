from django.conf import settings
from urllib.parse import urljoin, urlencode


class ComputerDataImporter(object):

    def __init__(self):
        pass

    def build_api_url(self, **kwargs):
        api_url = urljoin(settings.LOMADEE_API_URL, settings.LOMADEE_APP_TOKEN)

        # Specific path to 'Computer' category
        url = urljoin(api_url, 'offer/_category/6424')
        kwargs['sourceId'] = settings.LOMADEE_SOURCE_ID

        return '{}?{}'.format(url, urlencode(kwargs))
