from django.contrib import admin

from .models import StationLayout, StationLayoutQuarantine


class StationLayoutAdmin(admin.ModelAdmin):
    list_display = ('station', 'active_date')
    list_filter = ('station',)


class StationLayoutQuarantineAdmin(admin.ModelAdmin):
    list_display = ('station', 'active_date', 'email_verified', 'approved',
                    'reviewed')
    list_filter = ('station', 'email_verified', 'approved', 'reviewed')


admin.site.register(StationLayout, StationLayoutAdmin)
admin.site.register(StationLayoutQuarantine, StationLayoutQuarantineAdmin)
