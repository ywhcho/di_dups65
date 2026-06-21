from django.contrib import admin
from django.urls import include, path

from .views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', home_view, name='home'),
    path('equiv_ingr/', include('equiv_ingr.urls')),
]
