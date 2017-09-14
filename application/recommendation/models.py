from django.db import models


class UserState(models.Model):

    user = models.CharField(max_length=255, primary_key=True)
    state = models.CharField(max_length=50, default='welcome')

    class Meta:
        verbose_name = "UserState"
        verbose_name_plural = "UserStates"

    def __str__(self):
        return '{} - {}'.format(self.user, self.state)


class UserProfile(models.Model):

    user = models.CharField(max_length=255, primary_key=True)
    is_student = models.IntegerField(default=0)
    documents_sheets = models.IntegerField(default=0)
    image_video = models.IntegerField(default=0)
    performance = models.IntegerField(default=0)
    heavy_games = models.IntegerField(default=0)
    light_games = models.IntegerField(default=0)
    cost_benefit = models.IntegerField(default=0)

    class Meta:
        verbose_name = "UserProfile"
        verbose_name_plural = "UserProfiles"

    def __str__(self):
        return self.user
