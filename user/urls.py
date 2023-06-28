from django.urls import path
from .views import *

urlpatterns = [
    path('login', login),
    path('register', register),
    path('information', information),
    path('get_repair_info', worker_list),
    path('all_client', user_list),
    path('delete_user', delete_user),
    path('search_repair_info', search_worker),

    path('search_worker', search_worker),
    path('search_user', search_user),
    path('user_lease_info', user_lease_info),
    path('update_worker', update_worker_info),
    path('update_user', update_user_info),
    path('date', date_7),
]
