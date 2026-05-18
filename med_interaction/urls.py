from django.urls import path

from . import views

app_name = 'med_interaction'

urlpatterns = [
    path('check/', views.interaction_check, name='interaction_check'),
]
