from django.contrib import admin

from .models import MedInteractionMfname, MedicinesMedicine


@admin.register(MedInteractionMfname)
class MedInteractionMfnameAdmin(admin.ModelAdmin):
    list_display = ('wfco', 'ingrnd_t', 'kingrnd_t', 'cfno', 'fname')
    search_fields = ('wfco', 'ingrnd_t', 'kingrnd_t', 'cfno')


@admin.register(MedicinesMedicine)
class MedicinesMedicineAdmin(admin.ModelAdmin):
    list_display = ('wfco', 'htname', 'ingred', 'company', 'cfno', 'deriv2', 'ypri24')
    search_fields = ('wfco', 'htname', 'ingred', 'cfno')
