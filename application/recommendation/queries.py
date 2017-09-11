from django.db.models import Q
import numpy as np


QUERIES = {
    'cpu': {0: Q(cpu='i3'),
            1: Q(cpu='i5'),
            2: Q(cpu='i7')},
    'ram': {0: Q(ram__lte=4),
            1: Q(ram__gt=4, ram__lte=12),
            2: Q(ram__gt=12)},
    'disk': {0: Q(disk__lte=1000),
             1: Q(disk__gt=1000)},
}


def get_query(name, array):
    chosen = np.where(array)[0]
    return QUERIES[name][chosen[0]]
