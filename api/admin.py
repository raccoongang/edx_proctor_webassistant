from django.contrib import admin
from api.models import Exam, Permission, Student


class ExamAdmin(admin.ModelAdmin):
    pass


class PermissionAdmin(admin.ModelAdmin):
    pass


class StudentAdmin(admin.ModelAdmin):
    pass


admin.site.register(Exam, ExamAdmin)
admin.site.register(Permission, PermissionAdmin)
admin.site.register(Student, StudentAdmin)
