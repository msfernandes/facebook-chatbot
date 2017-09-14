from django.conf.urls import url
from recommendation import views

urlpatterns = [
    url(r'^$', views.WebhookView.as_view(), name='webhook'),
]
