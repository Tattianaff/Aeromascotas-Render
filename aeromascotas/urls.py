from django.urls import path # type: ignore
from . import views
from .views import solicitar_recuperacion, restablecer_contraseña


urlpatterns = [

    #Index general
    path('', views.index, name='index'),
    
    # Administrador
    path('index_administrador/', views.index_administrador, name='index_administrador'),
    path('administradores/', views.lista_administradores, name='lista_administradores'),
    path("perfil_administrador/", views.perfil_administrador, name="perfil_administrador"),
    path('administradores/editar/<int:id>/', views.editar_administrador, name='editar_administrador'),

    path('cliente/perfil_cliente_admin/<int:id>/', views.perfil_cliente_admin, name='perfil_cliente_admin'),
    path('clientes/editar_admin/<int:id>/', views.editar_cliente_admin, name='editar_cliente_admin'),

    # Aerolínea
    path('aerolineas/', views.lista_aerolineas, name='lista_aerolineas'),
    path('modificar_politicas/', views.modificar_politicas, name='modificar_politicas'),
    path('actualizar_politica/<int:id>/', views.actualizar_politica, name='actualizar_politica'),

    # Cliente
    path('index_cliente/', views.index_cliente, name='index_cliente'),
    path('cliente/perfil/', views.perfil_cliente, name='perfil_cliente'),
    path('ver_clientes/', views.ver_clientes, name='ver_clientes'),
    path('clientes/agregar/', views.agregar_cliente, name='agregar_cliente'),
    path('clientes/editar/<int:id>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/eliminar/<int:id>/', views.eliminar_cliente, name='eliminar_cliente'),

    # Destino
    path('destinos/', views.lista_destinos, name='lista_destinos'),
   
    # Origen
    path('origenes/', views.lista_origenes, name='lista_origenes'),
   
    # Mascota
    path('registrar_mascota/', views.registrar_mascota, name='registrar_mascota'),
    path('editar_mascota/<int:id>/', views.editar_mascota, name='editar_mascota'),
    path('mascotas/eliminar/<int:id>/', views.eliminar_mascota, name='eliminar_mascota'),
    path('perfil_mascota/<int:id>/', views.perfil_mascota, name='perfil_mascota'),
    path('ver_mascota/', views.ver_mascota, name='ver_mascota'),

    # Raza
    path('razas/', views.lista_razas, name='lista_razas'),
    
    # Servicio
    path('servicios/', views.lista_servicios, name='lista_servicios'),
    path('tarifas/', views.tarifas, name='tarifas'),
    path('tarifas_administrador/', views.tarifas_administrador, name='tarifas_administrador'),

    # Solicitud
    path('solicitudes/', views.lista_solicitudes, name='lista_solicitudes'),
    path('registrar_solicitud_completa/', views.registrar_solicitud_completa, name='registrar_solicitud_completa'),
    path('registrar_solicitud_especifica/', views.registrar_solicitud_especifica, name='registrar_solicitud_especifica'),
    path('ver_solicitudes/', views.ver_solicitudes, name='ver_solicitudes'),    
    path('cancelar_solicitud/<int:servicio_id>/', views.cancelar_solicitud, name="cancelar_solicitud"),
    path('cancelar_solicitud_admin/<int:servicio_id>/', views.cancelar_solicitud_admin, name="cancelar_solicitud_admin"),
    path('solicitudes/actualizar-estado/<int:solicitud_id>/', views.actualizar_estado_solicitud, name='actualizar_estado_solicitud'),
    path('editar_solicitud_completa/<int:id>/', views.editar_solicitud_completa, name='editar_solicitud_completa'),
    path('editar_solicitud_especifica/<int:id>/', views.editar_solicitud_especifica, name='editar_solicitud_especifica'),
    path('actualizar_notificacion/<int:solicitud_id>/', views.actualizar_notificacion_solicitud, name='actualizar_notificacion_solicitud'),
    path('detalle_solicitud/<int:solicitud_id>/', views.ver_detalle_solicitud, name='ver_detalle_solicitud'),
    path('asesoria/', views.asesoria, name='asesoria'),
    path('contar_solicitudes/', views.contar_solicitudes, name='contar_solicitudes'),
    #solicitudes_tipo
    path('contar_solicitudes_por_tipo/', views.contar_solicitudes_por_tipo, name='contar_solicitudes_por_tipo'),
    #actualizar_estado_solicitud
    path('actualizar_estado_solicitud/<int:solicitud_id>/', views.actualizar_estado_solicitud, name='actualizar_estado_solicitud'),
    #envio_documentos
    path('solicitudes/enviar_documentos/<int:solicitud_id>/', views.enviar_documentos_aprobado, name='enviar_documentos_aprobado'),

   
    #Inicio Sesion / Cerra Sesion
    path('inicio_sesion/', views.inicio_sesion, name='inicio_sesion'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),



    
    # Informes
    path('cliente/descargar_solicitudes/', views.descargar_solicitudes_pdf, name='descargar_solicitudes_pdf'),
    path('administracion/descargar_solicitudes/', views.descargar_todas_solicitudes_pdf, name='descargar_todas_solicitudes_pdf'),
    path('administracion/importar_solicitudes/', views.importar_solicitudes_excel, name='importar_solicitudes'),

    #Recuperar Contraseña
    path("recuperar/", solicitar_recuperacion, name="solicitar_recuperacion"),
    path("restablecer/<uidb64>/<token>/", restablecer_contraseña, name="restablecer_contraseña"),
]