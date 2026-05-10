"""
URL configuration for medsite project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('medicines/', include('medicines.urls')),
    path('accounts/', include('accounts.urls')),
    path('board/', include('board.urls')),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
]
