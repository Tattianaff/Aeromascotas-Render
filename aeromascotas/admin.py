from django.contrib import admin
from . models import Administrador, Aerolinea, Nacionalidad, Cliente, Destino, Origen, Raza, Mascota, Servicio, Solicitud

# Register your models here.


admin.site.register(Administrador)
admin.site.register(Aerolinea)
admin.site.register(Nacionalidad)
admin.site.register(Cliente)
admin.site.register(Destino)
admin.site.register(Origen)
admin.site.register(Raza)
admin.site.register(Mascota)
admin.site.register(Servicio)
admin.site.register(Solicitud)