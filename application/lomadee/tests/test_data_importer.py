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
    def test_get_data_404(self, requests_mock):
        response = MagicMock()
        response.json = lambda: json_mock_response(status=404)
        requests_mock.return_value = response

        data = self.importer.get_data()

        self.assertIsNone(data)

    @mock.patch('requests.get')
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

    @mock.patch('lomadee.data_importer.ComputerDataImporter.get_data')
    def test_get_valid_data(self, get_data_mock):
        return_value = [
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
             'product': {'userRating': {'rating': 8}}},
            {'id': '124405051',
             'name': 'Notebook Samsung Essentials E32 Intel Pentium 4GB 1TB '
                     'Tela LED HD 14 ´ Windows 10 - Preto',
             'link': 'http://product.redirect',
             'thumbnail': 'http://thumbnail.link',
             'price': 3888.90,
             'product': {'userRating': {'rating': 8}}},
        ]
        get_data_mock.return_value = return_value
        valid_data = self.importer.get_valid_data()
        self.assertEquals(len(valid_data), 2)
        self.assertGreater(len(return_value), len(valid_data))

    def test_has_method(self):
        self.assertTrue(self.importer._has('sub', 'substring'))
        self.assertFalse(self.importer._has('test', 'substring'))

    def test_get_method(self):
        self.assertEquals(('test', ),
                          self.importer._get('(test) regex', 'test regex'))
        self.assertIsNone(self.importer._get('(fail)', 'test regex'))

    def test_has_ssd(self):
        description = ('Notebook Samsung Essentials E32 Intel Core i3 4GB 1TB '
                       'Tela LED HD 14 ´ Windows 10 - Preto')
        self.assertFalse(self.importer.has_ssd(description))

        description = ('Notebook Samsung Essentials E32 Intel Core i3 4GB 1TB '
                       '128GB SSD Tela LED HD 14 ´ Windows 10 - Preto')
        self.assertTrue(self.importer.has_ssd(description))

    def test_has_gpu(self):
        description = ('Notebook Samsung Essentials E32 Intel Core i3 4GB 1TB '
                       'Tela LED HD 14 ´ Windows 10 - Preto')
        self.assertFalse(self.importer.has_gpu(description))

        description = ('Notebook Samsung Essentials E32 Intel Core i3 4GB 1TB '
                       'GeForce 1060 Tela LED HD 14 ´ Windows 10 - Preto')
        self.assertTrue(self.importer.has_gpu(description))

        description = ('Notebook Samsung Essentials E32 Intel Core i3 4GB 1TB '
                       'GTX 1060 Tela LED HD 14 ´ Windows 10 - Preto')
        self.assertTrue(self.importer.has_gpu(description))

        description = ('Notebook Samsung Essentials E32 Intel Core i3 4GB 1TB '
                       'NVIDEA 1060 Tela LED HD 14 ´ Windows 10 - Preto')
        self.assertTrue(self.importer.has_gpu(description))

        description = ('Notebook Samsung Essentials E32 Intel Core i3 4GB 1TB '
                       'Radeon RX 570 Tela LED HD 14 ´ Windows 10 - Preto')
        self.assertTrue(self.importer.has_gpu(description))

        description = ('Notebook Samsung Essentials E32 Intel Core i3 4GB 1TB '
                       'Placa de Video Dedicada Tela LED HD 14 ´ Windows 10 - '
                       'Preto')
        self.assertTrue(self.importer.has_gpu(description))

    def test_is_macbook(self):
        description = ('Notebook Samsung Essentials E32 Intel Core i3 4GB 1TB '
                       'Tela LED HD 14 ´ Windows 10 - Preto')
        self.assertFalse(self.importer.is_macbook(description))

        description = ('Apple Macbook Pro Retina 13.3 Mf839 Intel Core I5 '
                       '2.7ghz / 8gb Ram / 128gb Ssd / Os X Yosemite')
        self.assertTrue(self.importer.is_macbook(description))

    def test_get_ram(self):
        description = ('Notebook Samsung Essentials E32 Intel Core i3 4GB 1TB '
                       'Tela LED HD 14 ´ Windows 10 - Preto')
        self.assertEquals(4, self.importer.get_ram(description))

        description = ('Apple Macbook Pro Retina 13.3 Mf839 Intel Core I5 '
                       '2.7ghz / 8gb Ram / 128gb Ssd / Os X Yosemite')
        self.assertEquals(8, self.importer.get_ram(description))

        description = ('Notebook Samsung Essentials E32 Intel Core i3 1TB '
                       'Tela LED HD 14 ´ Windows 10 - Preto')
        self.assertIsNone(self.importer.get_ram(description))

    def test_get_disk(self):
        description = ('Notebook Samsung Essentials E32 Intel Core i3 4GB 1TB '
                       'Tela LED HD 14 ´ Windows 10 - Preto')
        self.assertEquals(1000, self.importer.get_disk(description))

        description = ('Apple Macbook Pro Retina 13.3 Mf839 Intel Core I5 '
                       '2.7ghz / 8gb Ram / 128gb Ssd / Os X Yosemite')
        self.assertEquals(128, self.importer.get_disk(description))

        description = ('Notebook Samsung Essentials E32 Intel Core i3 4GB '
                       'Tela LED HD 14 ´ Windows 10 - Preto')
        self.assertIsNone(self.importer.get_disk(description))

    def test_get_cpu(self):
        description = ('Notebook Samsung Essentials E32 Intel Core i3 4GB 1TB '
                       'Tela LED HD 14 ´ Windows 10 - Preto')
        self.assertEquals('i3', self.importer.get_cpu(description))

        description = ('Apple Macbook Pro Retina 13.3 Mf839 Intel Core I5 '
                       '2.7ghz / 8gb Ram / 128gb Ssd / Os X Yosemite')
        self.assertEquals('i5', self.importer.get_cpu(description))

        description = ('Notebook Samsung Essentials E32 Intel Pentium 4GB 1TB '
                       'Tela LED HD 14 ´ Windows 10 - Preto')
        self.assertIsNone(self.importer.get_cpu(description))

    def test_get_specs(self):
        description = ('Notebook Samsung Essentials E32 Intel Core i3 4GB 1TB '
                       'Tela LED HD 14 ´ Windows 10 - Preto')
        self.assertEquals(('i3', 4, 1000, False, False, False),
                          self.importer.get_specs(description))

        description = ('Apple Macbook Pro Retina 13.3 Mf839 Intel Core I5 '
                       '2.7ghz / 8gb Ram / 128gb Ssd / Os X Yosemite')
        self.assertEquals(('i5', 8, 128, True, False, True),
                          self.importer.get_specs(description))
