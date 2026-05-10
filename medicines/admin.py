from django.contrib import admin
from .models import Medicine, DrugInfo


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('htname', 'ingred', 'company')
    search_fields = ('htname', 'ingred', 'company')


@admin.register(DrugInfo)
class DrugInfoAdmin(admin.ModelAdmin):
    list_display = ('htname', 'ingred', 'company')
    search_fields = ('htname', 'ingred', 'company')
