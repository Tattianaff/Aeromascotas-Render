from django.db import models # type: ignore
from datetime import date

class Administrador(models.Model):
    nombre_completo = models.CharField(max_length=250)
    telefono = models.CharField(max_length=20)
    n_identificacion = models.CharField(max_length=20, unique=True)
    tipo_documento = models.CharField(max_length=20)
    contraseña = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    foto_perfil = models.ImageField(upload_to='admin/', null=True, blank=True)  # NUEVO

    def __str__(self):
        return self.nombre_completo


class Aerolinea(models.Model):
    nombre = models.CharField(max_length=50)
    contacto = models.CharField(max_length=50)
    requisitos = models.TextField()
    politicas = models.TextField()

    def __str__(self):
        return f"Política de {self.aerolinea.nombre}"


class Nacionalidad(models.Model):
    nombre_pais = models.CharField(max_length=50)



class Cliente(models.Model):
    foto_perfil = models.ImageField(upload_to='clientes/', null=True, blank=True)
    fecha_nacimiento = models.DateField()
    tipo_documento = models.CharField(max_length=20)
    n_documento = models.CharField(max_length=20, unique=True)
    nombres = models.CharField(max_length=45)
    apellidos = models.CharField(max_length=45)
    direccion = models.CharField(max_length=50)
    telefono = models.CharField(max_length=20)
    contraseña = models.CharField(max_length=128)
    correo = models.EmailField(unique=True)
    nacionalidad = models.ForeignKey(Nacionalidad, on_delete=models.CASCADE)


class Destino(models.Model):
    ciudad = models.CharField(max_length=50)
    nombre_aeropuerto = models.CharField(max_length=50)


class Origen(models.Model):
    ciudad = models.CharField(max_length=50)
    nombre_aeropuerto = models.CharField(max_length=50)

class Especie(models.Model):
    nombre_especie = models.CharField(max_length=20)

class Raza(models.Model):
    especie = models.ForeignKey(Especie, on_delete=models.CASCADE, null="True")
    nombre_raza = models.CharField(max_length=20)


class Mascota(models.Model):
    nombre = models.CharField(max_length=20)
    estado= models.CharField(max_length=20, default="Activa" )
    edad = models.CharField(max_length=60, null=True, blank=True) 
    fecha_nacimiento = models.DateField(null=True, blank=True)
    peso = models.IntegerField()
    tamaño = models.CharField(max_length=20)
    inf_medica = models.TextField()
    sexo = models.CharField(max_length=11)
    especie = models.ForeignKey(Especie, on_delete=models.SET_NULL, null=True)
    raza = models.ForeignKey(Raza, on_delete=models.SET_NULL, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    imagen = models.ImageField(upload_to='mascotas/', null=True, blank=True )

    def calcular_edad(self):
       
        if self.fecha_nacimiento:
            hoy = date.today()
            diferencia = hoy - self.fecha_nacimiento
            meses = diferencia.days // 30 

            if meses < 12:
                return f"{meses} meses" if meses > 0 else "Menos de 1 mes"
            else:
                edad_anios = meses // 12
                return f"{edad_anios} año" if edad_anios == 1 else f"{edad_anios} años"

        return "Desconocida"

    def save(self, *args, **kwargs):
    
        self.edad = self.calcular_edad() 
        super(Mascota, self).save(*args, **kwargs)  

class Servicio(models.Model):
    tipo_servicio = models.CharField(max_length=30)
    descripcion = models.TextField()
    tarifa = models.IntegerField()


class Solicitud(models.Model):
    estado = models.CharField(max_length=30, default="Pendiente")
    fecha = models.DateField(default=date.today)

    # Archivos
    vacunas = models.FileField(upload_to='solicitudes/vacunas/', null=True, blank=True)
    informacion_medica = models.FileField(upload_to='solicitudes/medica/', null=True, blank=True)
    certificado_salud = models.FileField(upload_to='solicitudes/certificado/', null=True, blank=True)
    pasaporte = models.FileField(upload_to='solicitudes/pasaporte/', null=True, blank=True)
    documento_cliente = models.FileField(upload_to='solicitudes/documentos_cliente/', null=True, blank=True)

    # Información del boleto (Opcional)
    boleto_vuelo = models.FileField(upload_to='solicitudes/boleto/', null=True, blank=True)
    n_vuelo=models.CharField(max_length=20, null=True, blank=True)
    duracion = models.TimeField(null=True, blank=True)
    destino = models.ForeignKey("Destino", on_delete=models.SET_NULL, null=True, blank=True)
    aerolinea = models.ForeignKey("Aerolinea", on_delete=models.SET_NULL, null=True, blank=True)
    origen = models.ForeignKey("Origen", on_delete=models.SET_NULL, null=True, blank=True)
    
    servicio = models.ForeignKey(Servicio, on_delete=models.SET_NULL, null=True, blank=True)
    mascota = models.ForeignKey("Mascota", on_delete=models.SET_NULL, null=True, blank=True)
    cliente = models.ForeignKey("Cliente", on_delete=models.SET_NULL, null=True, blank=True)
    administrador = models.ForeignKey("Administrador", on_delete=models.SET_NULL, null=True, blank=True)
    notificacion = models.ForeignKey("Notificacion", on_delete=models.SET_NULL, null=True, blank=True)


class Notificacion(models.Model):
    detalle = models.TextField()
