from django.contrib import admin
from lomadee import models


@admin.register(models.Computer)
class ComputerAdmin(admin.ModelAdmin):
    pass
