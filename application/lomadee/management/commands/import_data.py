from django.core.management.base import BaseCommand
from lomadee.data_importer import ComputerDataImporter


class Command(BaseCommand):
    def handle(self, *args, **options):
        importer = ComputerDataImporter()
        importer.save_data()
