from django.conf import settings
from urllib.parse import urljoin, urlencode
import requests


class ComputerDataImporter(object):

    def __init__(self):
        pass

    def build_api_url(self, **kwargs):
        api_url = urljoin(settings.LOMADEE_API_URL, settings.LOMADEE_APP_TOKEN)

        # Specific path to 'Computer' category
        url = urljoin('{}/'.format(api_url), 'offer/_category/6424')
        kwargs['sourceId'] = settings.LOMADEE_SOURCE_ID
        kwargs['size'] = 100

        return '{}?{}'.format(url, urlencode(kwargs))

    def get_data(self, url=None):
        if not url:
            url = self.build_api_url()

        data = requests.get(url).json()
        if data['requestInfo']['status'] != 'OK':
            return None

        final_data = []
        final_data.extend(data['offers'])
        pagination = data['pagination']

        if pagination['page'] < pagination['totalPage']:
            next_page_data = self.get_data(
                self.build_api_url(page=pagination['page'] + 1)
            )
            final_data.extend(next_page_data)
        return final_data
