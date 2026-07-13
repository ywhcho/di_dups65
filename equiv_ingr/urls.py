from django.urls import path

from . import views

app_name = 'equiv_ingr'

urlpatterns = [
    path('', views.search_view, name='search'),
    path('druginfo/', views.druginfo_detail, name='druginfo_detail'),
]
