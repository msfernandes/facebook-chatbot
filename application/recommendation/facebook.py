from django.conf import settings
from urllib.parse import urljoin, urlencode
import requests


def build_url(path='me/messages', **kwargs):
    api_url = urljoin(settings.FACEBOOK_API_URL, path)
    kwargs['access_token'] = settings.FACEBOOK_SECRET_TOKEN
    return '{}?{}'.format(api_url, urlencode(kwargs))


def send_message(recipient, message_type, message):
    url = build_url()
    payload = {
        'recipient': {'id': recipient},
        message_type: message
    }
    requests.post(url, json=payload)


def get_user_infos(user_id):
    url = build_url(user_id, fields='first_name,last_name')
    return requests.get(url).json()
