from django.contrib import admin
from models import *

class LeverancierAdmin(admin.ModelAdmin):
    list_display = ('naam','woonplaats','land','telefoon','contactpersoon')
    list_filter = ('woonplaats','land')
    search_fields = ('naam',)
    #ordering = ('naam')

class ArtikelAdmin(admin.ModelAdmin):
    list_display = ('naam','opbergplek','aantal','leverancier','datum','commentaar')
    list_filter = ('opbergplek','leverancier')
    search_fields = ('naam',)
    #ordering = ('naam')

class ApparatuurAdmin(admin.ModelAdmin):
    list_display = ('naam','opbergplek','aantal')
    #list_filter = ('opbergplek')
    search_fields = ('naam',)

class ReserveringAdmin(admin.ModelAdmin):
    list_display = ('cluster','artikel','aantal','datum','voldaan')
    list_filter = ('cluster','voldaan')
    search_fields = ('artikel',)
                 
class GebruiktAdmin(admin.ModelAdmin):
    list_display = ('persoon','artikel','aantal','datum','cluster')
    list_filter = ('persoon','cluster')
    #search_fields = ('artikel')
    #ordering = ('naam')

class BestelAdmin(admin.ModelAdmin):
    list_display = ('persoon','artikel','aantalbesteld','datumbesteld','levertijd','aantalgeleverd','datumgeleverd','voldaan')
    list_filter = ('persoon','voldaan')
    search_fields = ('artikel',)
    #ordering = ('naam') s

admin.site.register(Leverancier, LeverancierAdmin)
admin.site.register(Opbergplek)
admin.site.register(Artikel, ArtikelAdmin)
admin.site.register(Apparatuur, ApparatuurAdmin)
admin.site.register(Reservering, ReserveringAdmin)
admin.site.register(Gebruikt, GebruiktAdmin)
admin.site.register(Bestel, BestelAdmin)
