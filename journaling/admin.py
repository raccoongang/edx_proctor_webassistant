from django.contrib import admin
from journaling import models


class JournalingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'type', 'datetime', 'event', 'proctor', 'exam'
    )
    list_filter = ('type', 'event', 'proctor', 'datetime')
    search_fields = ('note', 'proctor_ip')
    readonly_fields = (
    'type', 'event', 'exam', 'proctor', 'datetime', 'proctor_ip')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(models.Journaling, JournalingAdmin)
