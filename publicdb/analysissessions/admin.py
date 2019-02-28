from django.contrib import admin

from . import models


@admin.register(models.AnalysisSession)
class AnalysisSessionAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    exclude = ('hash',)
    list_display = ('title', 'slug', 'pin', 'starts', 'ends', 'in_progress')


@admin.register(models.AnalyzedCoincidence)
class AnalyzedCoincidenceAdmin(admin.ModelAdmin):
    exclude = ('coincidence',)
    list_display = ('session', 'coincidence', 'student', 'is_analyzed')
    list_display_links = ('session', 'coincidence')
    list_filter = ('session', 'is_analyzed')


@admin.register(models.Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'session')
    list_filter = ('session',)


@admin.register(models.SessionRequest)
class SessionRequestAdmin(admin.ModelAdmin):
    list_display = ('cluster', 'school', 'name', 'start_date', 'events_created')
    list_filter = ('cluster', 'start_date')
