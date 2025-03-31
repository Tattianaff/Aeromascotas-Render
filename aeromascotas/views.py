from datetime import date, datetime
from email.message import EmailMessage
import json
import time
import hashlib
import base64
import pandas as pd # type: ignore
from django.contrib import messages  # type: ignore
from django.http import HttpResponse, JsonResponse # type: ignore
from django.shortcuts import render, get_object_or_404, redirect # type: ignore
from django.contrib.auth import logout # type: ignore
from django.urls import reverse # type: ignore
from django.views.decorators.cache import never_cache # type: ignore
from .models import Administrador, Cliente, Mascota, Raza, Nacionalidad, Aerolinea, Solicitud, Servicio, Destino, Origen, Especie, Notificacion
from django.contrib.auth.hashers import make_password # type: ignore
from django.contrib.auth.hashers import check_password # type: ignore
from .forms import MascotaForm, AerolineaForm
from django.views.decorators.csrf import csrf_protect # type: ignore
from django.core.mail import send_mail # type: ignore
from reportlab.lib.pagesizes import letter  # type: ignore
from reportlab.pdfgen import canvas # type: ignore
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode # type: ignore
from django.utils.encoding import force_bytes, force_str # type: ignore
from django.conf import settings # type: ignore
import qrcode # type: ignore
from io import BytesIO
from django.core.mail import EmailMessage
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt # type: ignore
from datetime import datetime, timedelta



# ================= Vista del Index General =================
@never_cache
def index(request):
    return render(request, 'index.html')




# ================= Administrador =================
@never_cache
def index_administrador(request):
    return render(request, 'index_administrador.html')

@never_cache
def lista_administradores(request):
    return render(request, 'administradores/lista.html')

@never_cache
def perfil_administrador(request):
    admin_id = request.session.get('id_ADMIN')  # Asegúrate de guardar esto en sesión al iniciar sesión

    if not admin_id:
        messages.error(request, "Debes iniciar sesión como administrador para ver tu perfil.")
        return redirect("inicio_sesion")

    administrador = get_object_or_404(Administrador, id=admin_id)

    return render(request, "perfil_administrador.html", {"administrador": administrador})


@never_cache
def editar_administrador(request, id):
    administrador = get_object_or_404(Administrador, id=id)

    if request.method == "POST":
        administrador.nombre_completo = request.POST.get("nombre_completo")
        administrador.telefono = request.POST.get("telefono")
        administrador.tipo_documento = request.POST.get("tipo_documento")
        administrador.n_identificacion = request.POST.get("n_identificacion")
        administrador.correo = request.POST.get("correo")

        # Procesar imagen si se sube una nueva
        foto_perfil = request.FILES.get("foto_perfil")
        if foto_perfil:
            administrador.foto_perfil = foto_perfil

        administrador.save()
        messages.success(request, "Tu perfil ha sido actualizado exitosamente.")
        return redirect("perfil_administrador")

    return render(request, "editar_administrador.html", {
        "administrador": administrador
    })


# ================= Aerolínea =================
@never_cache
def lista_aerolineas(request):
    return render(request, 'aerolineas/lista.html')

def modificar_politicas(request):
    aerolineas = Aerolinea.objects.all()  # 🔹 Obtener todas las aerolíneas

    if request.method == "POST":
        aerolinea_id = request.POST.get('aerolinea_id')  # 🔹 Obtener la aerolínea seleccionada
        aerolinea = get_object_or_404(Aerolinea, id=aerolinea_id)
        form = AerolineaForm(request.POST, instance=aerolinea)

        if form.is_valid():
            form.save()
            return redirect('modificar_politicas')  # 🔹 Redirige tras guardar

    else:
        form = AerolineaForm()

    return render(request, 'modificar_politicas.html', {
        'aerolineas': aerolineas,
        'form': form
    })

def actualizar_politica(request, id):
    aerolinea = get_object_or_404(Aerolinea, id=id)

    if request.method == "GET":
        return JsonResponse({"success": True, "politica": aerolinea.politicas})

    elif request.method == "POST":
        nueva_politica = request.POST.get("politica", "").strip()
        
        if nueva_politica:
            aerolinea.politicas = nueva_politica
            aerolinea.save()
            return JsonResponse({"success": True, "message": "Política actualizada correctamente."})
        
        return JsonResponse({"success": False, "message": "El campo no puede estar vacío."})
    
    return JsonResponse({"success": False, "message": "Método no permitido."})



# ================= Cliente =================

@never_cache
def index_cliente(request):
    id_cliente = request.session.get('id_CLIENTE', None)
    
    if not id_cliente:
        messages.add_message(request, messages.ERROR, "Error: Cliente no identificado en la sesión")
        return redirect('inicio_sesion')

    mascotas = Mascota.objects.filter(cliente_id=id_cliente)
    return render(request, 'index_cliente.html', {'mascotas': mascotas})

@never_cache
def agregar_cliente(request):
    nacionalidades = Nacionalidad.objects.all()

    if request.method == "POST":
        print("📌 Se recibió un formulario POST.") 

        nombres = request.POST.get("nombres")
        apellidos = request.POST.get("apellidos")
        fecha_nacimiento = request.POST.get("fecha_nacimiento")
        tipo_documento = request.POST.get("tipo_documento")
        n_documento = request.POST.get("n_documento")
        direccion = request.POST.get("direccion")
        telefono = request.POST.get("telefono")
        contraseña = request.POST.get("contraseña")
        correo = request.POST.get("correo")
        nacionalidad_id = request.POST.get("nacionalidad")

        print(f"📌 Datos recibidos: {nombres}, {apellidos}, {correo}")  

        if not all([nombres, apellidos, fecha_nacimiento, tipo_documento, n_documento, direccion, telefono, contraseña, correo, nacionalidad_id]):
            print("⚠️ Error: Campos vacíos detectados.")
            messages.error(request, "Todos los campos son obligatorios.")
            return render(request, "registrarse.html", {"nacionalidades": nacionalidades})

        # Validar edad mayor de 18 años
        try:
            fecha_obj = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
            edad = (date.today() - fecha_obj).days // 365
            if edad < 18:
                messages.error(request, "Debes ser mayor de 18 años para registrarte.")
                return render(request, "registrarse.html", {"nacionalidades": nacionalidades})
        except ValueError:
            messages.error(request, "Fecha de nacimiento inválida.")
            return render(request, "registrarse.html", {"nacionalidades": nacionalidades})

        if Cliente.objects.filter(n_documento=n_documento).exists():
            print("⚠️ Error: Documento duplicado.")
            messages.error(request, "El número de documento ya está registrado.")
            return render(request, "registrarse.html", {"nacionalidades": nacionalidades})

        if Cliente.objects.filter(correo=correo).exists():
            print("⚠️ Error: Correo duplicado.")
            messages.error(request, "El correo electrónico ya está registrado.")
            return render(request, "registrarse.html", {"nacionalidades": nacionalidades})

        try:
            nacionalidad = get_object_or_404(Nacionalidad, id=nacionalidad_id)
            print(f"✅ Nacionalidad encontrada: {nacionalidad}")
        except Exception as e:
            print(f"❌ Error al obtener la nacionalidad: {e}")
            messages.error(request, "Error con la nacionalidad seleccionada.")
            return render(request, "registrarse.html", {"nacionalidades": nacionalidades})

        contraseña_encriptada = make_password(contraseña)
        print(f"🔑 Contraseña encriptada: {contraseña_encriptada}")

        try:
            cliente = Cliente(
                nombres=nombres,
                apellidos=apellidos,
                fecha_nacimiento=fecha_nacimiento,
                tipo_documento=tipo_documento,
                n_documento=n_documento,
                direccion=direccion,
                telefono=telefono,
                contraseña=contraseña_encriptada,
                correo=correo,
                nacionalidad=nacionalidad
            )
            cliente.save()
            print(f"✅ Cliente {cliente.nombres} {cliente.apellidos} guardado correctamente.")
            
            try:
                send_mail(
                    subject="¡Bienvenido a Aeromascotas! 🐾",
                    message=(
                        f"Hola {cliente.nombres},\n\n"
                        "Gracias por registrarte en Aeromascotas. 🐶✈️\n"
                        "Tu cuenta ha sido creada exitosamente. Ya puedes gestionar tus mascotas y tus servicios.\n\n"
                        "¡Nos alegra tenerte a bordo!\n\n"
                        "El equipo de Aeromascotas 💙"
                    ),
                    from_email=None,  # usa DEFAULT_FROM_EMAIL del settings.py
                    recipient_list=[cliente.correo],
                    fail_silently=False,
                )
                print(f"📩 Correo de confirmación enviado a {cliente.correo}")
            except Exception as e:
                print(f"❌ Error al enviar correo de confirmación: {e}")

        except Exception as e:
            print(f"❌ Error al guardar cliente: {e}")
            messages.error(request, "Hubo un error al registrar el cliente.")
            return render(request, "registrarse.html", {"nacionalidades": nacionalidades})

        messages.success(request, "Cliente registrado exitosamente.")
        return redirect("inicio_sesion")

    return render(request, "registrarse.html", {"nacionalidades": nacionalidades})

@never_cache
def perfil_cliente(request):

    cliente_id = request.session.get('id_CLIENTE')  
    cliente = get_object_or_404(Cliente, id=cliente_id)

    # Verificar que el cliente esté autenticado
    if not cliente_id:
        messages.error(request, "Debes iniciar sesión para ver tu perfil.")
        return redirect("inicio_sesion")

    cliente = get_object_or_404(Cliente, id=cliente_id)  # Obtener cliente desde la base de datos

    return render(request, "perfil_cliente.html", {"cliente": cliente})

@never_cache
def perfil_cliente_admin(request, id):
    cliente = get_object_or_404(Cliente, id=id)

    return render(request, "perfil_cliente_admin.html", {"cliente": cliente})

@never_cache
def ver_clientes(request):
    clientes = Cliente.objects.all() 
    return render(request, 'ver_clientes.html', {"clientes": clientes})

@never_cache
def editar_cliente(request, id):
    # Obtener el ID del cliente desde la sesión
    cliente = get_object_or_404(Cliente, id=id)
    nacionalidades = Nacionalidad.objects.all()  # Cargar todas las nacionalidades
    
    if request.method == "POST":
        # Obtener los nuevos valores desde el formulario
        cliente.nombres = request.POST.get("nombres")
        cliente.apellidos = request.POST.get("apellidos")
        cliente.fecha_nacimiento = request.POST.get("fecha_nacimiento")
        cliente.tipo_documento = request.POST.get("tipo_documento")
        cliente.n_documento = request.POST.get("n_documento")
        cliente.direccion = request.POST.get("direccion")
        cliente.telefono = request.POST.get("telefono")
        cliente.correo = request.POST.get("correo")
        nacionalidad_id = request.POST.get("nacionalidad")
        foto_perfil = request.FILES.get("foto_perfil")  


        # Validar que la nacionalidad existe
        cliente.nacionalidad = get_object_or_404(Nacionalidad, id=nacionalidad_id)

        # Si se sube una nueva foto, actualizarla
        if foto_perfil:
            cliente.foto_perfil = foto_perfil

        # Guardar cambios
        cliente.save()

        messages.success(request, "Tu perfil ha sido actualizado exitosamente.")
        return redirect("perfil_cliente")  # Redirigir a la página principal del cliente después de editar

    return render(request, "editar_cliente.html", {
        "cliente": cliente, 
        "nacionalidades": nacionalidades
    })

@never_cache
def editar_cliente_admin(request, id):

    cliente = get_object_or_404(Cliente, id=id)  # Obtener cliente por ID
    nacionalidades = Nacionalidad.objects.all()  # Obtener todas las nacionalidades disponibles

    if request.method == "POST":
        # Obtener valores del formulario, manteniendo los actuales si no se envían nuevos
        cliente.nombres = request.POST.get("nombres", cliente.nombres)
        cliente.apellidos = request.POST.get("apellidos", cliente.apellidos)
        cliente.fecha_nacimiento = request.POST.get("fecha_nacimiento", cliente.fecha_nacimiento)
        cliente.tipo_documento = request.POST.get("tipo_documento", cliente.tipo_documento)
        cliente.n_documento = request.POST.get("n_documento", cliente.n_documento)
        cliente.direccion = request.POST.get("direccion", cliente.direccion)
        cliente.telefono = request.POST.get("telefono", cliente.telefono)
        cliente.correo = request.POST.get("correo", cliente.correo)

        # Validar que la nacionalidad exista antes de asignarla
        nacionalidad_id = request.POST.get("nacionalidad")
        if nacionalidad_id:
            cliente.nacionalidad = get_object_or_404(Nacionalidad, id=nacionalidad_id)

        # Verificar si se subió una nueva foto
        foto_perfil = request.FILES.get("foto_perfil")
        if foto_perfil:
            cliente.foto_perfil = foto_perfil

        # Guardar cambios en la base de datos
        cliente.save()
        messages.success(request, "Tu perfil ha sido actualizado exitosamente.")

        # Redirigir al perfil del cliente actualizado
        return redirect("perfil_cliente_admin", id=cliente.id)

    # Renderizar el formulario con la información actual del cliente
    return render(request, "editar_cliente_admin.html", {
        "cliente": cliente,
        "nacionalidades": nacionalidades
    })

@never_cache
def eliminar_cliente(request, id):
    return redirect('lista_clientes')



# ================= Mascota ========================================
@never_cache
def perfil_mascota(request, id):
    mascota = get_object_or_404(Mascota, id=id)
    return render(request, 'perfil_mascota.html', {'mascota': mascota})

from .models import Especie, Raza, Mascota  # Asegúrate de importar Especie

@never_cache
def registrar_mascota(request):
    print("➡ Vista registrar_mascota activada")
    cliente_id = request.session.get('id_CLIENTE')

    if not cliente_id:
        messages.error(request, "No se pudo identificar el cliente.")
        return redirect('inicio_sesion')

    especie_id = request.POST.get('especie') if request.method == 'POST' else None
    razas = Raza.objects.filter(especie_id=especie_id) if especie_id else []
    especies = Especie.objects.all()

    if request.method == 'POST':
        print("📥 Método POST detectado")

        if 'registrar' in request.POST:
            print("✅ Botón 'registrar' presionado")

            # Extraer datos del formulario
            nombre = request.POST.get('nombre')
            fecha_nacimiento_str = request.POST.get('fecha_nacimiento')
            peso = request.POST.get('peso')
            tamaño = request.POST.get('tamaño')
            inf_medica = request.POST.get('inf_medica')
            sexo = request.POST.get('sexo')
            raza_id = request.POST.get('raza')
            imagen = request.FILES.get('imagen')

            print(f"📦 Datos recibidos: {nombre}, {fecha_nacimiento_str}, {peso}, {tamaño}, {sexo}, {especie_id}, {raza_id}")

            # Validación básica
            if not all([nombre, fecha_nacimiento_str, peso, tamaño, inf_medica, sexo, especie_id, raza_id]):
                messages.error(request, "Todos los campos son obligatorios.")
            else:
                try:
                    fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, "%Y-%m-%d").date()
                    peso = int(peso)

                    if fecha_nacimiento > date.today():
                        messages.error(request, "La fecha de nacimiento no puede ser en el futuro.")
                    else:
                        mascota = Mascota(
                            nombre=nombre,
                            fecha_nacimiento=fecha_nacimiento,
                            peso=peso,
                            tamaño=tamaño,
                            inf_medica=inf_medica,
                            sexo=sexo,
                            especie_id=especie_id,
                            raza_id=raza_id,
                            cliente_id=cliente_id,
                            imagen=imagen
                        )
                        mascota.save()
                        print("✅ Mascota guardada correctamente")
                        messages.success(request, "Mascota registrada exitosamente.")
                        return redirect('ver_mascota')

                except ValueError as e:
                    print("❌ Error de conversión:", e)
                    messages.error(request, "Verifica los campos de peso o fecha.")
                except Exception as e:
                    print("❌ Error al guardar mascota:", e)
                    messages.error(request, f"Ocurrió un error: {e}")

    return render(request, 'registrar_mascota.html', {
        'razas': razas,
        'especies': especies,
        'id_cliente': cliente_id
    })

@never_cache
def editar_mascota(request, id):
    mascota = get_object_or_404(Mascota, id=id)
    especie_id = mascota.especie.id if mascota.especie else None
    razas = Raza.objects.filter(especie_id=especie_id)

    if request.method == "POST":
        especie_id = request.POST.get('especie')
        form = MascotaForm(request.POST, request.FILES, instance=mascota, especie_id=especie_id)

        if form.is_valid():
            mascota = form.save(commit=False)

            fecha_nacimiento_str = request.POST.get('fecha_nacimiento')
            if fecha_nacimiento_str:
                mascota.fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, "%Y-%m-%d").date()
                mascota.edad = mascota.calcular_edad()

            if not mascota.cliente:
                cliente_id = request.session.get('cliente_id') or request.session.get('id_CLIENTE')
                if cliente_id:
                    mascota.cliente = Cliente.objects.get(id=cliente_id)

            mascota.save()
            return redirect('ver_mascota')

    else:
        form = MascotaForm(instance=mascota, especie_id=especie_id)

    return render(request, 'editar_mascota.html', {
        'form': form,
        'mascota': mascota,
        'razas': form.fields['raza'].queryset,
        'id_cliente': request.session.get('cliente_id')
    })

@never_cache
def eliminar_mascota(request, id):
    mascota = get_object_or_404(Mascota, id=id)

    # Verificar si la mascota tiene solicitudes activas (no canceladas)
    solicitudes_activas = Solicitud.objects.filter(mascota=mascota).exclude(estado="Cancelado")

    if solicitudes_activas.exists():
        return JsonResponse({
            "success": False,
            "message": f"La mascota '{mascota.nombre}' no puede ser eliminada porque tiene solicitudes activas."
        })

    # Si no tiene solicitudes activas, eliminar la mascota
    mascota.delete()

    return JsonResponse({
        "success": True,
        "message": f"La mascota '{mascota.nombre}' ha sido eliminada exitosamente."
    })

@never_cache
def ver_mascota(request):
    id_cliente = request.session['id_CLIENTE'] 

    mascotas = Mascota.objects.filter(cliente_id=id_cliente)
    return render(request, 'ver_mascota.html', {'mascotas': mascotas})



# ================= Raza ====================
@never_cache
def lista_razas(request):
    return render(request, 'razas/lista.html')



# ================= Servicio =================
@never_cache
def lista_servicios(request):
    return render(request, 'servicios/lista.html')

@never_cache
def tarifas(request):
    servicios = Servicio.objects.all()  
    return render(request, 'tarifas.html', {'servicios': servicios})

@never_cache
def tarifas_administrador(request):
    servicios = Servicio.objects.all()
    
    if request.method == 'POST':
        for servicio in servicios:
            nuevo_precio = request.POST.get(f'tarifa_{servicio.id}')
            if nuevo_precio:
                servicio.tarifa = int(nuevo_precio)  
                servicio.save()

        return redirect('tarifas_administrador')  
    
    return render(request, 'tarifas_administrador.html', {'servicios': servicios})



# ================= Solicitud =================
@never_cache #admin
def lista_solicitudes(request):
    solicitudes = Solicitud.objects.select_related('servicio', 'cliente').all()
    return render(request, 'solicitudes.html', {'solicitudes': solicitudes})

@never_cache
def registrar_solicitud_completa(request):
    id_cliente = request.session.get('id_CLIENTE', None)
    
    if not id_cliente:
        return redirect("inicio_sesion")

    cliente = get_object_or_404(Cliente, id=id_cliente)
    mascotas = Mascota.objects.filter(cliente=cliente, estado="Activa")
    aerolineas = Aerolinea.objects.all()
    destinos = Destino.objects.all()
    origenes = Origen.objects.all()
    servicio = get_object_or_404(Servicio, id=1)
    administrador = Administrador.objects.first()

    # Horas y minutos para el select
    horas = [f"{h:02d}" for h in range(24)]
    minutos = [f"{m:02d}" for m in range(0, 60, 5)]

    if request.method == "POST":
        mascota_id = request.POST.get("mascota")
        aerolinea_id = request.POST.get("aerolinea")
        destino_id = request.POST.get("destino")
        origen_id = request.POST.get("origen")
        hora = request.POST.get("hora")
        minuto = request.POST.get("minuto")
        n_vuelo = request.POST.get("n_vuelo")

        duracion = f"{hora}:{minuto}" if hora and minuto else None

        # Archivos
        vacunas = request.FILES.get("vacunas")
        informacion_medica = request.FILES.get("informacion_medica")
        certificado_salud = request.FILES.get("certificado_salud")
        boleto_vuelo = request.FILES.get("boleto_vuelo")
        pasaporte = request.FILES.get("pasaporte")
        documento_cliente = request.FILES.get("documento_cliente")

        # Validar campos obligatorios
        if not all([mascota_id, aerolinea_id, destino_id, origen_id, hora, minuto]):
            messages.error(request, "Por favor completa todos los campos obligatorios.")
            return redirect("registrar_solicitud_completa")

        # Obtener relaciones con validación
        try:
            mascota = Mascota.objects.get(id=int(mascota_id), cliente=cliente)
            aerolinea = Aerolinea.objects.get(id=int(aerolinea_id))
            destino = Destino.objects.get(id=int(destino_id))
            origen = Origen.objects.get(id=int(origen_id))
        except Exception as e:
            print(f"❌ Error al obtener datos relacionados: {e}")
            messages.error(request, "Error en la selección de datos. Por favor verifica los campos.")
            return redirect("registrar_solicitud_completa")

        # Verificar si ya existe una solicitud parecida
        duplicada = Solicitud.objects.filter(
            cliente=cliente,
            mascota=mascota,
            servicio=servicio,
            aerolinea=aerolinea,
            destino=destino,
            origen=origen,
            duracion=duracion,
            estado="Pendiente"
        ).exists()

        if duplicada:
            messages.warning(request, "Ya has registrado una solicitud similar que está en estado pendiente.")
            return redirect("ver_solicitudes")

        # Crear la solicitud
        solicitud = Solicitud.objects.create(
            cliente=cliente,
            administrador=administrador,
            servicio=servicio,
            mascota=mascota,
            aerolinea=aerolinea,
            destino=destino,
            origen=origen,
            duracion=duracion,
            n_vuelo=n_vuelo,
            vacunas=vacunas,
            informacion_medica=informacion_medica,
            certificado_salud=certificado_salud,
            boleto_vuelo=boleto_vuelo,
            pasaporte=pasaporte,
            documento_cliente=documento_cliente,
            estado="Pendiente"
        )

        enviar_correo_con_qr(cliente, servicio)  # Enviar QR por correo

        messages.success(request, "¡Solicitud registrada exitosamente!")
        return redirect("ver_solicitudes")

    return render(request, "registrar_solicitud_completa.html", {
        "mascotas": mascotas,
        "aerolineas": aerolineas,
        "destinos": destinos,
        "origenes": origenes,
        "servicios": Servicio.objects.all(),
        "horas": horas,
        "minutos": minutos,
    })


@never_cache
def editar_solicitud_completa(request, id):
    solicitud = get_object_or_404(Solicitud, id=id)

    if request.method == 'POST':
        solicitud.mascota_id = request.POST.get('mascota')
        solicitud.aerolinea_id = request.POST.get('aerolinea')
        solicitud.destino_id = request.POST.get('destino')
        solicitud.origen_id = request.POST.get('origen')
        solicitud.duracion = request.POST.get('duracion')
        solicitud.n_vuelo = request.POST.get('n_vuelo')

        # Archivos adjuntos (solo actualiza si se envía un nuevo archivo)
        if request.FILES.get('vacunas'):
            solicitud.vacunas = request.FILES['vacunas']
        if request.FILES.get('certificado_salud'):
            solicitud.certificado_salud = request.FILES['certificado_salud']
        if request.FILES.get('informacion_medica'):
            solicitud.informacion_medica = request.FILES['informacion_medica']
        if request.FILES.get('boleto_vuelo'):
            solicitud.boleto_vuelo = request.FILES['boleto_vuelo']
        if request.FILES.get('pasaporte'):
            solicitud.pasaporte = request.FILES['pasaporte']
        if request.FILES.get('documento_cliente'):
            solicitud.documento_cliente = request.FILES['documento_cliente']

        solicitud.save()
        messages.success(request, "¡La solicitud fue actualizada exitosamente!")
        return redirect('ver_solicitudes')

    context = {
        'form': solicitud,
        'id': solicitud.id,
        'mascotas': Mascota.objects.filter(cliente=solicitud.cliente),
        'aerolineas': Aerolinea.objects.all(),
        'destinos': Destino.objects.all(),
        'origenes': Origen.objects.all(),
        # 'servicios': Servicio.objects.all(), ← ya no es necesario si no se edita
    }
    return render(request, 'editar_solicitud_completa.html', context)


@never_cache
def registrar_solicitud_especifica(request):
    id_cliente = request.session.get('id_CLIENTE')

    if not id_cliente:
        return redirect("login")  

    cliente = get_object_or_404(Cliente, id=id_cliente) 
    mascotas = Mascota.objects.filter(cliente=cliente, estado="Activa")  
    aerolineas = Aerolinea.objects.all()
    destinos = Destino.objects.all()
    origenes = Origen.objects.all()
    servicios = Servicio.objects.exclude(id=1)  # Omitir el servicio con ID 1
    administrador = Administrador.objects.first()

    if request.method == "POST":
        servicio_id = request.POST.get("servicio")

        # 🔹 Filtrar sólo los valores válidos de mascota
        mascota_ids = [value for value in request.POST.getlist("mascota") if value.strip()]
        mascota_id = mascota_ids[0] if mascota_ids else None  # Tomar solo el primero válido

        vacunas = request.FILES.get("vacunas")
        certificado_salud = request.FILES.get("certificado_salud")

        servicio = get_object_or_404(Servicio, id=servicio_id) if servicio_id else None
        mascota = get_object_or_404(Mascota, id=mascota_id, cliente=cliente) if mascota_id else None

        print("POST data:", request.POST)
        print("Mascota seleccionada:", mascota_id)
        print("Servicio seleccionado:", servicio_id)

        solicitud = Solicitud.objects.create(
            cliente=cliente,
            administrador=administrador,
            servicio=servicio,
            mascota=mascota,
            vacunas=vacunas,
            certificado_salud=certificado_salud,
            estado="Pendiente",
        )

        return redirect("ver_solicitudes")

    return render(request, "registrar_solicitud_especifica.html", {
        "servicios": servicios,  
        "mascotas": mascotas,  
        "aerolineas": aerolineas,
        "destinos": destinos,
        "origenes": origenes,
    })

@never_cache
def editar_solicitud_especifica(request, id):
    solicitud = get_object_or_404(Solicitud, id=id)

    if request.method == 'POST':
        solicitud.mascota_id = request.POST.get("mascota")

        # Verifica el tipo de servicio
        tipo_servicio = solicitud.servicio.tipo_servicio.lower()

        # Si es certificado de salud o apoyo emocional, puede tener vacunas
        if 'salud' in tipo_servicio or 'apoyo emocional' in tipo_servicio:
            if request.FILES.get("vacunas"):
                solicitud.vacunas = request.FILES["vacunas"]

        # Si es apoyo emocional, puede tener certificado de salud también
        if 'apoyo emocional' in tipo_servicio:
            if request.FILES.get("certificado_salud"):
                solicitud.certificado_salud = request.FILES["certificado_salud"]

        solicitud.save()
        messages.success(request, "¡La solicitud fue actualizada correctamente!")
        return redirect("ver_solicitudes")

    context = {
        "solicitud": solicitud,
        "mascotas": Mascota.objects.filter(cliente=solicitud.cliente, estado="Activa"),
    }
    return render(request, "editar_solicitud_especifica.html", context)

@never_cache  # cliente
def ver_solicitudes(request):
    id_cliente = request.session.get('id_CLIENTE')

    if not id_cliente:
        return redirect("inicio_sesion")

    solicitudes = Solicitud.objects.filter(cliente_id=id_cliente).select_related("servicio", "mascota", "notificacion")

    response = render(request, "ver_solicitudes.html", {
        "solicitudes": solicitudes
    })
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@never_cache
def cancelar_solicitud(request, servicio_id):
    servicio = get_object_or_404(Solicitud, id=servicio_id)
    
    # Solo permite cancelar si el servicio está pendiente
    if servicio.estado.lower() == "pendiente":
        servicio.estado = "Cancelado"
        servicio.save()
        return redirect("ver_solicitudes")
    else:
        url = reverse("ver_solicitudes") + "?error=1"
        return redirect(url)

@never_cache
@csrf_exempt
def cancelar_solicitud_admin(request, servicio_id):
    print("➡️ Entró a la vista cancelar_solicitud_admin")
    print("Método:", request.method)

    solicitud = get_object_or_404(Solicitud, id=servicio_id)
    print(f"🟡 Estado actual: '{solicitud.estado}'")
    print(f"➡️ Comparación da: {solicitud.estado.strip().lower() == 'pendiente'}")

    if request.method == "POST":
        if solicitud.estado.strip().lower() == "pendiente":
            try:
                data = json.loads(request.body)
                motivo = data.get("motivo_cancelacion", "").strip()
                print(f"📝 Motivo recibido: {motivo}")

                solicitud.estado = "Cancelado"
                solicitud.save()

                if solicitud.notificacion:
                    solicitud.notificacion.detalle = motivo
                    solicitud.notificacion.save()
                else:
                    noti = Notificacion.objects.create(detalle=motivo)
                    solicitud.notificacion = noti
                    solicitud.save()

                # HTML personalizado
                html_message = f"""
                <h2 style="color:#712cf9;">🐾 ¡Hola {solicitud.cliente.nombres}!</h2>
                <p>Te informamos que tu solicitud para el servicio 
                <strong>“{solicitud.servicio.tipo_servicio}”</strong> ha sido 
                <span style="color:red;"><strong>cancelada</strong></span> 🛑.</p>

                <p><strong>📝 Motivo de la cancelación:</strong><br>{motivo}</p>

                <p style="margin-top: 20px;">
                Gracias por confiar en <strong style="color:#712cf9;">AeroMascotas</strong> 🐶✈️
                </p>
                <hr>
                <p style="font-size: 13px; color: #888;">
                Si tienes dudas, contáctanos respondiendo este correo.
                </p>
                """

                plain_message = strip_tags(html_message)

                send_mail(
                    subject="❌ Cancelación de solicitud - AeroMascotas",
                    message=plain_message,
                    from_email="aeromascotas@noreply.com",
                    recipient_list=[solicitud.cliente.correo],
                    html_message=html_message,
                    fail_silently=False
                )

                print("✅ Solicitud cancelada correctamente")
                return JsonResponse({"status": "ok"})

            except Exception as e:
                print("❌ Error:", e)
                return JsonResponse({"status": "error", "mensaje": str(e)}, status=500)
        else:
            print("⚠️ No está pendiente, no se cancela")
            return JsonResponse({"status": "error", "mensaje": "No se puede cancelar una solicitud que no está pendiente."}, status=400)

    # Por si acaso entra con GET
    if solicitud.estado.strip().lower() != "pendiente":
        url = reverse("lista_solicitudes") + "?error=1"
        return redirect(url)

    return redirect("lista_solicitudes")


@never_cache #admin
@csrf_protect
def actualizar_estado_solicitud(request, solicitud_id):
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        solicitud.estado = nuevo_estado
        solicitud.save()
    return redirect('lista_solicitudes')

@never_cache
def actualizar_notificacion_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    detalle = request.POST.get("detalle", "").strip()

    if solicitud.notificacion:
        noti = solicitud.notificacion
        noti.detalle = detalle
        noti.save()
    else:
        noti = Notificacion.objects.create(detalle=detalle)
        solicitud.notificacion = noti
        solicitud.save()

    return redirect('lista_solicitudes')

@never_cache
def ver_detalle_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    return render(request, 'detalle_solicitud.html', {
        'solicitud': solicitud
    })

@never_cache
def asesoria(request):
    return render(request, 'asesoria.html')

@never_cache
def contar_solicitudes(request):
    total = Solicitud.objects.count()
    return JsonResponse({'total':total})

@never_cache
def contar_solicitudes_por_tipo(request):
    tipos_servicio = {
        "Servicio Completo": 1,
        "Certificado de Vacunas": 2,
        "Certificado de Salud": 3,
        "Apoyo Emocional": 4,
    }

    data = {}
    for nombre, id_servicio in tipos_servicio.items():
        cantidad = Solicitud.objects.filter(servicio__id=id_servicio).count()
        data[nombre] = cantidad

    return JsonResponse(data)



# ================= Destino =================
@never_cache
def lista_destinos(request):
    return render(request, 'destinos/lista.html')

# ================= Origen =================
@never_cache
def lista_origenes(request):
    return render(request, 'origenes/lista.html')



# ================= Inicio Sesión =================
@never_cache
def inicio_sesion(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contraseña = request.POST.get('contraseña')

        # Verificar cliente
        cliente = Cliente.objects.filter(correo=correo).first()
        if cliente and check_password(contraseña, cliente.contraseña):
            request.session['id_CLIENTE'] = cliente.id
            request.session.modified = True
            return redirect('index_cliente')

        # Verificar administrador
        administrador = Administrador.objects.filter(correo=correo).first()
        if administrador and contraseña == administrador.contraseña:
            request.session['id_ADMIN'] = administrador.id
            request.session.modified = True
            return redirect('index_administrador')

        # Si no se encuentran credenciales válidas
        messages.add_message(request, messages.ERROR, "Credenciales incorrectas. Inténtalo de nuevo.")
        return redirect('inicio_sesion')

    return render(request, 'inicio_sesion.html')

# ================= Cerrar Sesión =================
@never_cache
def cerrar_sesion(request):
    logout(request)
    request.session.flush()
    request.session.clear_expired()
    request.session.modified = True

    response = redirect('index')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


# ================= Exportes =================

#Cliente
def descargar_solicitudes_pdf(request):
    id_cliente = request.session.get('id_CLIENTE', None)
    
    if not id_cliente:
        return HttpResponse("Error: Cliente no identificado", status=400)

    solicitudes = Solicitud.objects.filter(cliente_id=id_cliente)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="mis_solicitudes.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    p.drawString(100, 750, "Mis Solicitudes")

    y = 730
    for solicitud in solicitudes:
        p.drawString(100, y, f"ID: {solicitud.id}, Fecha: {solicitud.fecha}, Estado: {solicitud.estado}")
        y -= 20

    p.showPage()
    p.save()
    return response

#Admin
def descargar_todas_solicitudes_pdf(request):
    solicitudes = Solicitud.objects.all()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="todas_solicitudes.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    p.drawString(100, 750, "Todas las Solicitudes")

    y = 730
    for solicitud in solicitudes:
        cliente_id = solicitud.cliente_id if solicitud.cliente_id else "No identificado"
        p.drawString(100, y, f"Cliente: {cliente_id} - ID: {solicitud.id}, Fecha: {solicitud.fecha}, Estado: {solicitud.estado}")
        y -= 20

    p.showPage()
    p.save()
    return response


# ================= Importes =================

#Admin
def importar_solicitudes_excel(request):
    if request.method == 'POST' and request.FILES.get('archivo_excel'):
        archivo = request.FILES['archivo_excel']
        
        print("Archivo recibido:", archivo)  # Verifica si el archivo llega

        try:
            df = pd.read_excel(archivo)

            print("Primeras filas del DataFrame:\n", df.head())  # Verifica el contenido del archivo

            solicitudes_creadas = []
            for index, row in df.iterrows():
                solicitud = Solicitud(
                    id=row['ID'],
                    fecha=row['Fecha'],
                    estado=row['Estado'],
                    cliente_id=row['Cliente_ID']
                )
                solicitudes_creadas.append(solicitud)

            Solicitud.objects.bulk_create(solicitudes_creadas)  # Guarda en la base de datos
            print("Solicitudes creadas:", Solicitud.objects.count())  # Cuenta registros en la tabla

            return redirect('index_administrador')  # Redirige después de importar
        except Exception as e:
            print("Error en la importación:", e)  # Muestra el error si falla
            return HttpResponse(f"Error al importar: {e}", status=400)

    return render(request, 'solicitudes.html')



# ================= Recuperar Contraseña =================

def generar_token(usuario):
    """Genera un token único basado en el ID del usuario y el tiempo actual."""
    data = f"{usuario.id}{int(time.time())}".encode()
    return base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode()[:32]

# SE SOLICITA RECUPERACIÓN

def solicitar_recuperacion(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        usuario = Cliente.objects.filter(correo__iexact=email).first()
        
        if usuario:
            uid = urlsafe_base64_encode(force_bytes(usuario.id))
            token = generar_token(usuario)
            enlace = request.build_absolute_uri(reverse("restablecer_contraseña", args=[uid, token]))

            send_mail(
            "Recuperación de contraseña - Aeromascotas",  
            f"""
            ¡Hola! 🐾  

            Hemos recibido una solicitud para restablecer tu contraseña.  
            Si fuiste tú, haz clic en el siguiente enlace para establecer una nueva contraseña:  
             {enlace}  

            Por seguridad, este enlace expirará en unos minutos.  
            Si no solicitaste este cambio, puedes ignorar este mensaje.  

            🐾✨ ¡Gracias por confiar en Aeromascotas!  
            El equipo de Aeromascotas 🛫🐾  
            """,
            settings.DEFAULT_FROM_EMAIL,
            [usuario.correo],
            fail_silently=False,
        )

        messages.success(request, " ¡Listo! Te hemos enviado un correo con las instrucciones para restablecer tu contraseña. 🐶🐱")
    
    return render(request, "formulario_reseteo_contraseña.html")

# RESTABLECER CONTRASEÑA

def restablecer_contraseña(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        cliente = Cliente.objects.get(id=uid)
    except (Cliente.DoesNotExist, ValueError, TypeError):
        cliente = None

    if cliente:
        if request.method == "POST":
            new_password1 = request.POST.get("new_password1")
            new_password2 = request.POST.get("new_password2")

            if new_password1 and new_password1 == new_password2:
                cliente.contraseña = make_password(new_password1)  
                cliente.save()
                messages.success(request, "Tu contraseña ha sido restablecida correctamente.")
                return redirect("inicio_sesion")
            else:
                messages.error(request, "Las contraseñas no coinciden.")

        return render(request, "reseteo_contraseña_confirmada.html", {"validlink": True})
    
    return render(request, "reseteo_contraseña_confirmada.html", {"validlink": False})

def generar_qr_pago(texto):
    qr = qrcode.make(texto)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    return buffer.getvalue()

def enviar_correo_con_qr(cliente, servicio):
    monto = servicio.tarifa

    # Texto que aparecerá al escanear el QR (puede usarse con la app de Nequi)
    texto_qr = (
        f"Pago AeroMascotas\n"
        f"Valor: ${monto:,.0f}\n"
        f"Nequi: 3195850772\n"
        f"Referencia: {cliente.id}-{servicio.id}"
    )

    # Generar imagen del QR
    qr_bytes = generar_qr_pago(texto_qr)

    # Cuerpo del correo
    mensaje = f"""
Hola {cliente.nombres},

Gracias por registrar tu solicitud con AeroMascotas. Adjuntamos el código QR con el valor a pagar por el servicio completo.

📌 Servicio: {servicio.tipo_servicio}
💰 Valor: ${monto:,.0f}
📱 Número Nequi: 3195850772

Puedes escanear el QR adjunto para ver estos datos desde tu celular y realizar el pago directamente por Nequi.

¡Gracias por confiar en nosotros!
"""

    # Envío del correo
    email = EmailMessage(
        subject="Registro de Solicitud - Código QR de pago",
        body=mensaje,
        to=[cliente.correo]
    )
    email.attach("codigo_qr_pago.png", qr_bytes, "image/png")
    email.send()


# ================= Actualizar Estado Solicitud =================
@never_cache
def actualizar_estado_solicitud(request, solicitud_id):
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        solicitud.estado = nuevo_estado
        solicitud.save()

        cliente = solicitud.cliente
        tipo_servicio = solicitud.servicio.tipo_servicio

        # Mensaje HTML amigable con emojis
        mensaje_html = f"""
        <h2 style="font-family: Arial, sans-serif;">🐾 ¡Hola {cliente.nombres.capitalize()}!</h2>
        <p>Te informamos que tu solicitud para el servicio <strong>“{tipo_servicio}”</strong> ha sido actualizada ✨.</p>
        <p>🟢 <strong>Nuevo estado:</strong> {nuevo_estado}</p>
        <p>Gracias por confiar en <strong>AeroMascotas</strong> 🐶✈️</p>
        <hr>
        <p style="font-size: small;">Si tienes dudas, contáctanos respondiendo este correo.</p>
        """

        send_mail(
            subject='📦 Cambio de estado de tu solicitud - AeroMascotas',
            message=strip_tags(mensaje_html),  # versión plana del mensaje
            html_message=mensaje_html,  # versión HTML
            from_email='no-reply@aeromascotas.com',
            recipient_list=[cliente.correo],
            fail_silently=False,
        )

        messages.success(request, 'Estado actualizado y correo enviado correctamente.')

    return redirect('lista_solicitudes')


# ================= Enviar Documentos Aprobados =================
@never_cache
def enviar_documentos_aprobado(request, solicitud_id):
    if request.method == 'POST':
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        cliente = solicitud.cliente

        tipo_servicio = solicitud.servicio.tipo_servicio
        nombre_cliente = cliente.nombres.capitalize()  # Ajusta si es otro campo

        # 💌 Mensaje con HTML + emojis
        mensaje_html = f"""
        <div style="font-family: Arial, sans-serif; padding: 15px;">
          <h2 style="color: #00aaff;">🐶✈️ ¡Hola {nombre_cliente}!</h2>
          <p>Te compartimos los documentos correspondientes a tu servicio <strong>“{tipo_servicio}”</strong>.</p>

          <p style="font-size: 16px;">📎 Los documentos adjuntos contienen información importante para el viaje de tu mascota.</p>

          <p style="margin-top: 20px;">Gracias por confiar en <strong style="color: #009688;">AeroMascotas</strong>, ¡tu compañero de aventuras peludas! 🐾</p>

          <p style="font-size: 13px; color: #888;">🐕🐈🐇 Si tienes alguna duda, no dudes en escribirnos.</p>
          <hr>
          <p style="font-size: 11px; color: #aaa;">✈️ AeroMascotas | Viajar con tu mascota, más fácil que nunca 🐾</p>
        </div>
        """

        # 📧 Email con HTML
        email = EmailMessage(
            subject='📎 Documentos de tu solicitud completada - AeroMascotas',
            body=strip_tags(mensaje_html),  # versión de respaldo (sin HTML)
            from_email='no-reply@aeromascotas.com',
            to=[cliente.correo],
        )
        email.content_subtype = 'html'  # Indica que es HTML
        # Adjuntar archivos
        for archivo in request.FILES.getlist('documentos'):
            email.attach(archivo.name, archivo.read(), archivo.content_type)

        # Enviar correo
        email.send()

        # ✅ Actualizar estado
        solicitud.estado = 'Completado'
        solicitud.save()

        return HttpResponse('Correo enviado y estado actualizado.')

    return HttpResponse('Método no permitido', status=405)