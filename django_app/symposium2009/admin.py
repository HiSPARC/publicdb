from django.contrib import admin
from models import *

class AnalyzedCoincidenceAdmin(admin.ModelAdmin):
    exclude = ('coincidence',)
    list_display = ('coincidence', 'student', 'is_analyzed')
    list_filter = ('is_analyzed', 'student')

admin.site.register(AnalyzedCoincidence, AnalyzedCoincidenceAdmin)
admin.site.register(Student)
