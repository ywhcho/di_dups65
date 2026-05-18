from django.contrib import admin

from .models import Mfname, Mintef


@admin.register(Mfname)
class MfnameAdmin(admin.ModelAdmin):
    list_display = ('wfco', 'fname', 'igrno1', 'igrno2', 'igrno3', 'igrno4')
    search_fields = ('wfco', 'fname', 'igrno1', 'igrno2', 'igrno3', 'igrno4')


@admin.register(Mintef)
class MintefAdmin(admin.ModelAdmin):
    list_display = ('igrno_a', 'igrno_b', 'irisk')
    search_fields = ('igrno_a', 'igrno_b', 'irisk', 'idesc', 'ireco')
