from django.urls import path

from . import views

app_name = 'equiv_htname'

urlpatterns = [
    path('', views.search_view, name='search'),
]
