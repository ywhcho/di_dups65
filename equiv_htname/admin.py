from django.contrib import admin

from .models import MedicinesMedicine, MedInteractionMfname


@admin.register(MedicinesMedicine)
class MedicinesMedicineAdmin(admin.ModelAdmin):
    list_display = ('wfco', 'htname', 'ingr_t', 'company', 'cfno', 'atc', 'deriv2', 'ypri24')
    search_fields = ('htname', 'wfco', 'ingr_t')


@admin.register(MedInteractionMfname)
class MedInteractionMfnameAdmin(admin.ModelAdmin):
    list_display = ('wfco', 'ingr_t', 'cfno', 'atc', 'deriv2', 'ypri24')
    search_fields = ('wfco', 'ingr_t')
