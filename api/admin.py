from django.contrib import admin
from api import models


class CommentInline(admin.TabularInline):
    """
    Comment inline class
    """
    model = models.Comment


class ExamAdmin(admin.ModelAdmin):
    """
    Exam admin class
    """
    list_display = ('exam_code', 'organization', 'exam_id', 'course_id',
                    'first_name', 'last_name', 'exam_status',
                    'username', 'exam_start_date', 'exam_end_date')
    list_filter = ('exam_status',)
    search_fields = ['exam_code', 'exam_id', 'first_name', 'last_name',
                     'course_id', 'user_id', 'username', 'email']
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
                'exam_id', 'course_id', 'user_id', 'first_name', 'last_name',
                'username', 'email')
        }),
        ('Additional', {
            'fields': (
                'event', 'course_organization', 'course_identify',
                'course_run',
                'exam_status')
        }),
    )
    inlines = [CommentInline]


class EventSessionAdmin(admin.ModelAdmin):
    """
    Event Session admin class
    """
    list_display = (
        'testing_center', 'course_id', 'course_event_id', 'proctor', 'status',
        'start_date', 'hash_key', 'end_date')
    list_filter = ('proctor', 'status')
    search_fields = (
        'testing_center', 'course_id', 'course_event_id', 'start_date',
        'end_date')
    readonly_fields = ('hash_key', 'start_date', 'end_date')


class PermissionAdmin(admin.ModelAdmin):
    """
    Pemission admin class
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


admin.site.register(models.Exam, ExamAdmin)
admin.site.register(models.InProgressEventSession, EventSessionAdmin)
admin.site.register(models.ArchivedEventSession, EventSessionAdmin)
admin.site.register(models.Permission, PermissionAdmin)
admin.site.register(models.Student, StudentAdmin)
