from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models
# Register your models here.


@admin.register(models.Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('first_name', 'last_name', 'username')


@admin.register(models.Aseguradora)
class AseguradoraAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nro_poliza')


@admin.register(models.Reembolso)
class ReembolsoAdmin(admin.ModelAdmin):
    list_display = ('id',)


@admin.register(models.CartaAval)
class CartaAvalAdmin(admin.ModelAdmin):
    list_display = ('id',)


@admin.register(models.SolicitudReembolso)
class SolicitudReembolsoAdmin(admin.ModelAdmin):
    list_display = ('id', 'estatus',)


@admin.register(models.SolicitudCartaAval)
class SolicitudCartaAvalAdmin(admin.ModelAdmin):
    list_display = ('id', 'estatus',)