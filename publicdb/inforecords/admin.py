from django.contrib import admin
from django.utils.safestring import mark_safe

from . import models


@admin.register(models.Cluster)
class ClusterAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'parent', 'country')
    list_filter = ('country',)
    ordering = ['number']


class ContactInline(admin.StackedInline):
    model = models.Contact
    extra = 0  # this stops empty forms being shown
    max_num = 0  # this removes the add more button
    can_delete = False


class StationInline(admin.StackedInline):
    model = models.Station
    extra = 0  # this stops empty forms being shown
    max_num = 0  # this removes the add more button
    can_delete = False


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email_work_link')
    list_max_show_all = 400

    def last_name(self, obj):
        if obj.prefix_surname:
            return f"{obj.surname}, {obj.prefix_surname}"
        else:
            return "%s" % obj.surname

    def email_work_link(self, obj):
        return mark_safe("<a href='mailto:{email}'>{email}</a>".format(email=obj.email_work))


@admin.register(models.Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('number', 'name')
    ordering = ['number']


@admin.register(models.Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'cluster', 'contactinformation',
                    'contact')
    search_fields = ('number', 'name', 'cluster__name')
    list_filter = ('cluster__country',)
    list_per_page = 200


@admin.register(models.ContactInformation)
class ContactInformationAdmin(admin.ModelAdmin):

    def owner_name(self, obj):
        return obj.contact_owner

    list_display = ('owner_name', 'street_1', 'postalcode', 'city', 'type')
    list_filter = ('city',)
    list_max_show_all = 400

    def type(self, obj):
        return obj.type

    inlines = (ContactInline, StationInline)


@admin.register(models.Pc)
class PcAdmin(admin.ModelAdmin):
    list_display = ('station', 'name', 'is_active', 'is_test', 'ip', 'url',
                    'keys')
    list_filter = ('is_active', 'is_test')
    ordering = ('station',)
    list_per_page = 200


admin.site.register(models.Profession)
admin.site.register(models.PcType)
