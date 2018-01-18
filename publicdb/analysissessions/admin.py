from django.contrib import admin

from .models import (AnalysisSession, AnalyzedCoincidence, SessionRequest,
                     Student)


class AnalysisSessionAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    exclude = ('hash',)
    list_display = ('title', 'slug', 'pin', 'starts', 'ends', 'in_progress')


class AnalyzedCoincidenceAdmin(admin.ModelAdmin):
    exclude = ('coincidence',)
    list_display = ('session', 'coincidence', 'student', 'is_analyzed')
    list_display_links = ('session', 'coincidence')
    list_filter = ('session', 'is_analyzed')


class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'session')
    list_filter = ('session',)


class SessionRequestAdmin(admin.ModelAdmin):
    list_display = ('cluster', 'school', 'name', 'start_date',
                    'events_created')
    list_filter = ('cluster', 'start_date')


admin.site.register(AnalysisSession, AnalysisSessionAdmin)
admin.site.register(AnalyzedCoincidence, AnalyzedCoincidenceAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(SessionRequest, SessionRequestAdmin)
