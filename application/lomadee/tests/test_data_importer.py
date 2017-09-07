from django.test import TestCase, override_settings
from lomadee.data_importer import ComputerDataImporter


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
