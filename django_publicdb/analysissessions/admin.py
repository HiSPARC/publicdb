from django.contrib import admin
from models import *

class AnalysisSessionAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    exclude = ('hash',)
    list_display = ('title', 'slug', 'hash', 'starts', 'ends',
                    'in_progress')

class AnalyzedCoincidenceAdmin(admin.ModelAdmin):
    exclude = ('coincidence',)
    list_display = ('coincidence', 'student', 'is_analyzed')
    list_filter = ('is_analyzed', 'student')


admin.site.register(AnalysisSession, AnalysisSessionAdmin)
admin.site.register(AnalyzedCoincidence, AnalyzedCoincidenceAdmin)
admin.site.register(Student)
