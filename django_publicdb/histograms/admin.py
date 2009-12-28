from django.contrib import admin
from models import *

class GeneratorStateAdmin(admin.ModelAdmin):
    list_display = ('check_last_run', 'check_is_running', 'update_last_run',
                    'update_is_running')

admin.site.register(Summary)
admin.site.register(DailyHistogram)
admin.site.register(HistogramType)
admin.site.register(GeneratorState, GeneratorStateAdmin)
