from django.urls import path

from .views import *

app_name = 'jobs'
urlpatterns = [
    path('', index, name='index'),
    path('results/', results, name='results'),
    path('redirect/<int:job_id>/', redirect, name='redirect'),
]
