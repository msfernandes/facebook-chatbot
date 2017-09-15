from numpy import genfromtxt
from django.conf import settings
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from lomadee import models
from django.db.models import Q
import numpy as np
import os


QUERIES = {
    'cpu': {0: Q(cpu='i3'),
            1: Q(cpu='i5'),
            2: Q(cpu='i7')},
    'ram': {0: Q(ram__lte=4),
            1: Q(ram__gt=4, ram__lte=12),
            2: Q(ram__gt=12)},
    'disk': {0: Q(),
             1: Q(disk__gte=1000)},
}


def get_query(name, array):
    chosen = np.where(array)[0]
    if len(chosen):
        return QUERIES[name][chosen[0]]
    else:
        return QUERIES[name][0]


class Classifier():

    def __init__(self):
        self.classifier = self._classifier(self.trainset_input(),
                                           self.trainset_output())

    def _load_csv(self, filename):
        path = os.path.join(settings.BASE_DIR, 'recommendation/' + filename)
        return genfromtxt(path, delimiter=',')

    def trainset_input(self):
        # Returns a np.array with 7 columns: is_student, documents_sheets,
        # image_video, performance, heavy_game, light_games and cost_benefit
        return self._load_csv('trainset-input.csv')

    def trainset_output(self):
        # Returns a np.array with 11 columns: i3, i5, i7, low_ram, medium_ram,
        # high_ram, has_ssd, has_gpu, large_disk, is_macbook,
        # better_price
        return self._load_csv('trainset-output.csv')

    def _classifier(self, x_train, y_train):
        classifier = MLPClassifier(hidden_layer_sizes=(11, 14, 18),
                                   max_iter=5000)
        classifier.fit(self.trainset_input(), self.trainset_output())
        return classifier

    def classify(self, is_student=0, documents_sheets=0, image_video=0,
                 performance=0, heavy_games=0, light_games=0, cost_benefit=0):
        return self.classifier.predict([[
            is_student, documents_sheets, image_video, performance,
            heavy_games, light_games, cost_benefit
        ]])

    def suggest(self, **kwargs):
        suggestion_profile = self.classify(**kwargs)[0]
        computers = models.Computer.objects.filter(
            get_query('cpu', suggestion_profile[:3]),
            get_query('ram', suggestion_profile[3:6]),
            QUERIES['disk'][suggestion_profile[8:9].item()],
            is_macbook=bool(suggestion_profile[9]),
            has_ssd=bool(suggestion_profile[6]),
            has_gpu=bool(suggestion_profile[7]),
        )
        if suggestion_profile[10]:
            order_by = 'price'
        else:
            order_by = '-price'
        return computers.order_by(order_by)[:3]

    def test(self):
        X_train, X_test, y_train, y_test = train_test_split(
            self.trainset_input(),
            self.trainset_output()
        )
        classifier = self._classifier(X_train, y_train)
        predictions = classifier.predict(X_test)
        print(classifier)
        print(classification_report(y_test, predictions))
