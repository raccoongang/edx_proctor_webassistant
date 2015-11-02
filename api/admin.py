from django.contrib import admin
from api.models import Exam, Permission, Student


class ExamAdmin(admin.ModelAdmin):
    list_display = ('exam_code', 'organization', 'exam_id', 'course_id',
                    'first_name', 'last_name', 'exam_status',
                    'exam_start_date', 'exam_end_date')
    list_filter = ('exam_status',)
    search_fields = ['exam_code', 'exam_id', 'first_name', 'last_name',
                     'course_id']

    fieldsets = (
        (None, {
            'fields': (
                'exam_code', 'organization', 'duration', 'reviewed_exam',
                'reviewer_notes', 'exam_password', 'exam_sponsor', 'exam_name',
                'ssi_product')
        }),
        ('Org Extra', {
            'fields': (
                'exam_start_date', 'exam_end_date', 'no_of_students',
                'exam_id', 'course_id', 'first_name', 'last_name')
        }),
        ('Additional', {
            'fields': (
                'course_organization', 'course_identify', 'course_run',
                'exam_status')
        }),
    )


class PermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'object_id', 'object_type')
    list_filter = ('user', 'object_type')
    search_fields = ['user', 'object_id', 'object_type']


class StudentAdmin(admin.ModelAdmin):
    list_display = ('sso_id', 'email', 'first_name', 'last_name')
    search_fields = ['sso_id', 'email', 'first_name', 'last_name']


admin.site.register(Exam, ExamAdmin)
admin.site.register(Permission, PermissionAdmin)
admin.site.register(Student, StudentAdmin)
