from django.urls import path
from . import views

app_name = 'med_dup'

urlpatterns = [
    path('duplicate/', views.duplicate_check, name='duplicate_check'),
]
