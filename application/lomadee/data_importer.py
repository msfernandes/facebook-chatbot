from django.conf import settings
from urllib.parse import urljoin, urlencode
from lomadee import models
from django.db import transaction
import re
import requests
import requests_cache


requests_cache.install_cache('lomadee_cache')


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

    def get_valid_data(self):
        all_data = self.get_data()
        valid_data = []
        for data in all_data:
            cpu, ram, disk, _, _, _ = self.get_specs(data['name'])
            if None not in (cpu, disk, ram, data['price']):
                valid_data.append(data)

        return valid_data

    def save_data(self):
        data = self.get_valid_data()
        empty_database = not models.Computer.objects.all().exists()
        for computer_data in data:
            self.create_object(computer_data, empty_database)

    @transaction.atomic
    def create_object(self, data, empty_database=True):
        if empty_database:
            computer = models.Computer()
            computer.id = data['id']
        else:
            computer = models.Computer.objects.get_or_create(
                id=data['id'],
                defaults={'name': data['name'],
                          'price': data['price'],
                          'thumbnail': data['thumbnail'],
                          'link': data['link']}
            )[0]

        specs = self.get_specs(data['name'])
        computer.name = data['name']
        computer.price = data['price']
        computer.thumbnail = data['thumbnail']
        computer.link = data['link']
        computer.cpu = specs[0]
        computer.ram = specs[1]
        computer.disk = specs[2]
        computer.is_macbook = specs[3]
        computer.has_gpu = specs[4]
        computer.has_ssd = specs[5]

        product = data.get('product', None)
        if product:
            computer.rating = data['product']['userRating']['rating']

        computer.save()
        return computer

    def get_specs(self, description):
        cpu = self.get_cpu(description)
        ram = self.get_ram(description)
        disk = self.get_disk(description)
        is_macbook = self.is_macbook(description)
        has_gpu = self.has_gpu(description)
        has_ssd = self.has_ssd(description)
        return (cpu, ram, disk, is_macbook, has_gpu, has_ssd)

    def get_cpu(self, description):
        groups = self._get('(i3|i5|i7)', description)
        if groups:
            return groups[0]

    def get_disk(self, description):
        groups = self._get('\s(\d{1})\s?(tb|tera)|\s(\d{3,4})\s?(hd|gb)',
                           description)
        if groups:
            tb, _, gb, _ = groups
            if tb:
                return int(tb) * 1000
            else:
                return int(gb)

    def get_ram(self, description):
        groups = self._get('\s(\d{1,2})\s?(gb|ram|ddr)', description)
        if groups:
            return int(groups[0])

    def is_macbook(self, description):
        return self._has('apple|macbook', description)

    def has_gpu(self, description):
        return self._has('geforce|gtx|dedicad[ao]|nvidea|radeon|graphics',
                         description)

    def has_ssd(self, description):
        return self._has('ssd|solid state', description)

    def _has(self, regex, description):
        match = re.search(regex, description.lower())
        if match:
            return True
        else:
            return False

    def _get(self, regex, description):
        match = re.search(regex, description.lower())
        if match:
            return match.groups()
        else:
            return None
