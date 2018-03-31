from django.contrib import admin

from . import models


@admin.register(models.StationLayout)
class StationLayoutAdmin(admin.ModelAdmin):
    list_display = ('station', 'active_date')
    list_filter = ('station',)


@admin.register(models.StationLayoutQuarantine)
class StationLayoutQuarantineAdmin(admin.ModelAdmin):
    list_display = ('station', 'active_date', 'email_verified', 'approved',
                    'reviewed')
    list_filter = ('station', 'email_verified', 'approved', 'reviewed')
