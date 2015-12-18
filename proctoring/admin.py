from django.contrib import admin
from proctoring import models


class CourseAdmin(admin.ModelAdmin):
    list_display = ('display_name',)
    list_filter = ('course_org',)
    search_fields = ('display_name',)

    def has_add_permission(self, request):
        return False


class CommentInline(admin.TabularInline):
    """
    Comment inline class
    """
    model = models.Comment


class ExamAdmin(admin.ModelAdmin):
    """
    Exam admin class
    """
    list_display = ('exam_code', 'organization', 'exam_id', 'course',
                    'first_name', 'last_name', 'exam_status',
                    'username', 'exam_start_date', 'exam_end_date')
    list_filter = ('exam_status', 'course')
    search_fields = ['exam_code', 'exam_id', 'first_name', 'last_name',
                     'user_id', 'username', 'email']
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
                'exam_id', 'user_id', 'first_name', 'last_name',
                'username', 'email')
        }),
        ('Additional', {
            'fields': (
                'event',
                'course',
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


admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.Exam, ExamAdmin)
admin.site.register(models.InProgressEventSession, EventSessionAdmin)
admin.site.register(models.ArchivedEventSession, EventSessionAdmin)
