from django.test import TestCase, override_settings
from lomadee.data_importer import ComputerDataImporter
from mock import MagicMock
import mock


def json_mock_response(status='OK', page=1, total_page=1):
    return {
        'requestInfo': {'status': status, 'message': 'SUCCESS'},
        'pagination': {'page': page, 'size': 10, 'totalSize': 10,
                       'totalPage': total_page},
        'offers': [
            {'id': '124405051',
             'name': 'Notebook Samsung Essentials E32 Intel Core i3 4GB 1TB '
                     'Tela LED HD 14 ´ Windows 10 - Preto',
             'link': 'http://product.redirect',
             'thumbnail': 'http://thumbnail.link',
             'price': 3888.90,
             'product': {'userRating': {'rating': 8}}}
        ]
    }


class ComputerDataImporterTestCase(TestCase):

    def setUp(self):
        self.importer = ComputerDataImporter()

    @override_settings(LOMADEE_API_URL='http://lomadee.api/',
                       LOMADEE_APP_TOKEN='1234',
                       LOMADEE_SOURCE_ID='123')
    def test_build_url(self):
        self.assertEquals(
            self.importer.build_api_url(),
            'http://lomadee.api/1234/offer/_category/6424?'
            'sourceId=123&size=100'
        )

    @override_settings(LOMADEE_API_URL='http://lomadee.api/',
                       LOMADEE_APP_TOKEN='1234',
                       LOMADEE_SOURCE_ID='123')
    def test_build_url_extra_params(self):
        self.assertEquals(
            self.importer.build_api_url(page=2),
            'http://lomadee.api/1234/offer/_category/6424?'
            'page=2&sourceId=123&size=100'
        )

    @mock.patch('requests.get')
    @override_settings(LOMADEE_API_URL='http://lomadee.api/',
                       LOMADEE_APP_TOKEN='1234',
                       LOMADEE_SOURCE_ID='123')
    def test_get_data(self, requests_mock):
        response = MagicMock()
        response.json = lambda: json_mock_response()
        requests_mock.return_value = response

        data = self.importer.get_data()

        self.assertEquals(data, [
            {'id': '124405051',
             'name': 'Notebook Samsung Essentials E32 Intel Core i3 4GB 1TB '
                     'Tela LED HD 14 ´ Windows 10 - Preto',
             'link': 'http://product.redirect',
             'thumbnail': 'http://thumbnail.link',
             'price': 3888.90,
             'product': {'userRating': {'rating': 8}}}
        ])

    @mock.patch('requests.get')
    @override_settings(LOMADEE_API_URL='http://lomadee.api/',
                       LOMADEE_APP_TOKEN='1234',
                       LOMADEE_SOURCE_ID='123')
    def test_get_data_404(self, requests_mock):
        response = MagicMock()
        response.json = lambda: json_mock_response(status=404)
        requests_mock.return_value = response

        data = self.importer.get_data()

        self.assertIsNone(data)

    @mock.patch('requests.get')
    @override_settings(LOMADEE_API_URL='http://lomadee.api/',
                       LOMADEE_APP_TOKEN='1234',
                       LOMADEE_SOURCE_ID='123')
    def test_get_data_pagination(self, requests_mock):
        response1 = MagicMock()
        response1.json = lambda: json_mock_response(total_page=2)
        response2 = MagicMock()
        response2.json = lambda: json_mock_response(page=2, total_page=2)
        requests_mock.side_effect = [response1, response2]

        data = self.importer.get_data()

        self.assertEquals(data, [
            {'id': '124405051',
             'name': 'Notebook Samsung Essentials E32 Intel Core i3 4GB 1TB '
                     'Tela LED HD 14 ´ Windows 10 - Preto',
             'link': 'http://product.redirect',
             'thumbnail': 'http://thumbnail.link',
             'price': 3888.90,
             'product': {'userRating': {'rating': 8}}},
            {'id': '124405051',
             'name': 'Notebook Samsung Essentials E32 Intel Core i3 4GB 1TB '
                     'Tela LED HD 14 ´ Windows 10 - Preto',
             'link': 'http://product.redirect',
             'thumbnail': 'http://thumbnail.link',
             'price': 3888.90,
             'product': {'userRating': {'rating': 8}}}
        ])
