from django.db import models

# Create your models here.


class Computer(models.Model):

    CPU_I3 = 'i3'
    CPU_I5 = 'i5'
    CPU_I7 = 'i7'
    CPU_CHOICES = (
        (CPU_I3, 'Intel Core i3'),
        (CPU_I5, 'Intel Core i5'),
        (CPU_I7, 'Intel Core i7'),
    )

    name = models.CharField(max_length=255)
    price = models.FloatField()
    thumbnail_url = models.URLField()
    cpu = models.CharField(choices=CPU_CHOICES, max_length=2)
    ram = models.IntegerField(default=2)
    disk = models.IntegerField(default=0)
    is_macbook = models.BooleanField(default=False)
    has_gpu = models.BooleanField(default=False)
    has_ssd = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Computer"
        verbose_name_plural = "Computers"

    def __str__(self):
        return self.name
