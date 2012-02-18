from django.contrib import admin
from models import *


class AnalysisSessionAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    exclude = ('hash',)
    list_display = ('title', 'slug', 'hash', 'starts', 'ends', 'in_progress')


class AnalyzedCoincidenceAdmin(admin.ModelAdmin):
    exclude = ('coincidence',)
    list_display = ('session', 'coincidence', 'student', 'is_analyzed')
    list_display_links = ('session', 'coincidence')
    list_filter = ('session', 'is_analyzed', 'student')


class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'session')
    list_filter = ('session',)


class SessionRequestAdmin(admin.ModelAdmin):
    lis_filter = ('email',)


admin.site.register(AnalysisSession, AnalysisSessionAdmin)
admin.site.register(AnalyzedCoincidence, AnalyzedCoincidenceAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(SessionRequest, SessionRequestAdmin)
