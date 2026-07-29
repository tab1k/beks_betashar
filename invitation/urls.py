from django.urls import path

from . import views

app_name = 'invitation'

urlpatterns = [
    path('', views.index, name='index'),
    path('rsvp/', views.rsvp, name='rsvp'),
]
