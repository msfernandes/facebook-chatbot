from django.contrib import admin
from lomadee import models


@admin.register(models.Computer)
class ComputerAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'cpu', 'ram', 'disk',
                    'is_macbook', 'has_gpu', 'has_ssd')
