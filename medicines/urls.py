from django.urls import path
from . import views

app_name = 'medicines'

urlpatterns = [
    path('duplicate/', views.duplicate_check, name='duplicate_check'),
    path('druginfo/', views.druginfo_list, name='druginfo_list'),
    path('druginfo/<int:pk>/', views.druginfo_detail, name='druginfo_detail'),
]
