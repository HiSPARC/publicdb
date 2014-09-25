from django.contrib import admin
from models import *


class AdminUpdateAdmin(admin.ModelAdmin):
    exclude = ('version',)
    list_display = ('queue', 'version')
    list_filter = ('queue',)


class UserUpdateAdmin(admin.ModelAdmin):
    exclude = ('version',)
    list_display = ('queue', 'version')
    list_filter = ('queue',)


class InstallerUpdateAdmin(admin.ModelAdmin):
    exclude = ('version',)
    list_display = ('queue', 'version')
    list_filter = ('queue',)


admin.site.register(UpdateQueue)
admin.site.register(AdminUpdate, AdminUpdateAdmin)
admin.site.register(UserUpdate, UserUpdateAdmin)
admin.site.register(InstallerUpdate, InstallerUpdateAdmin)
