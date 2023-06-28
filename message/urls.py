from django.urls import path
from .views import *

urlpatterns = [
    path('message_list', user_message_list),
    path('user_message_send', user_message_send),
    path('read_message', user_message_reading),
    path('make_appointment', make_appointment),
    path('send', message_test),
    path('appointment_list', appointment_list),
    path('appointment_statistics', appointment_statistics),
    path('maintenance_statistics', maintenance_statistics),
]
