from django.contrib import admin

from . import models


@admin.register(models.AdminUpdate, models.UserUpdate, models.InstallerUpdate)
class UpdateAdmin(admin.ModelAdmin):
    exclude = ('version',)
    list_display = ('queue', 'version')
    list_filter = ('queue',)


admin.site.register(models.UpdateQueue)
