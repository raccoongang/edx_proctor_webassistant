from django.contrib import admin

from person import models


class PermissionAdmin(admin.ModelAdmin):
    """
    Permission admin class
    """
    list_display = ('user', 'object_id', 'object_type', 'role')
    list_filter = ('user', 'object_type', 'role')
    search_fields = ['user', 'object_id', 'object_type', 'role']


class StudentAdmin(admin.ModelAdmin):
    """
    Student admin class
    """
    list_display = ('sso_id', 'email', 'first_name', 'last_name')
    search_fields = ['sso_id', 'email', 'first_name', 'last_name']


admin.site.register(models.Permission, PermissionAdmin)
admin.site.register(models.Student, StudentAdmin)