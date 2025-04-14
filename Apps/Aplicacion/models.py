from django.contrib.auth.models import AbstractUser
from django.db import models
# from django.core.validators import MinValueValidator
from django.core.validators import MinValueValidator, RegexValidator
from .choices import tipo_parientes,roles,estatus
# Create your models here.


class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('analista', 'Analista'),
        ('cliente', 'Cliente'),
    )

    username = models.CharField(
        'Cédula',
        max_length=20,
        unique=True,
        primary_key=True,
        validators=[
            RegexValidator(
                regex='^\d+$',
                message='La cédula debe contener solo números',
                code='invalid_username'
            )
        ]
    )
    first_name = models.CharField(
        'Nombres',
        max_length=255,
        blank=False,  # Hacer obligatorio
        null=False
    )
    last_name = models.CharField(
        'Apellidos',
        max_length=255,
        blank=False,  # Hacer obligatorio
        null=False
    )
    email = models.EmailField(
        'Correo electrónico',
        unique=True,  # Asegurar que el email sea único
        blank=False,  # Hacer obligatorio
        null=False
    )
    fecha_nacimiento = models.DateField(
        'Fecha de nacimiento',
        blank=False,  # Hacer obligatorio
        null=False
    )
    rol = models.CharField(
        'Rol',
        max_length=20,
        choices=ROLES,
        default='cliente'  # Rol por defecto
    )
    tipo_cedula = models.CharField(
        'Tipo de cédula',
        max_length=1,
        choices=[('V', 'Venezolano'), ('E', 'Extranjero')],
        default='V'
    )

    REQUIRED_FIELDS = [
        "email",
        "first_name",
        "last_name",
        "fecha_nacimiento"
    ]

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Aseguradora(models.Model):
    nombre = models.CharField(
        'Nombre de la aseguradora',
        max_length=255,
        blank=False,
        null=False
    )
    nro_poliza = models.IntegerField(
        'Numero de polizas',
        validators=[MinValueValidator(1)],
        blank=False,
        null=False
    )

    def __str__(self):
        return f'{self.nombre}'

class Titular(models.Model):
    username = models.OneToOneField(
        Usuario,
        on_delete = models.CASCADE
    )
    aseguradora = models.ForeignKey(
        Aseguradora,
        on_delete=models.PROTECT
    )
    telefono = models.IntegerField(
        'Telefono',
        blank=False,
        null=False
    )
    telefono_opcional = models.IntegerField(
        'Telefono opcional',
        blank=True,
        null=True
    )
    correo = models.CharField(
        'correo electronico',
        max_length=255,
        blank=False,
        null=False
    )
    vigencia_desde = models.DateField(
        'Vigencia desde',
        blank=False,
        null=False
    )
    vigencia_hasta = models.DateField(
        'vigencia hasta',
        blank=False,
        null=False
    )

    def __str__(self):
        return f'{self.username}'

class Familiar(models.Model):
    username = models.OneToOneField(
        Usuario,
        on_delete = models.CASCADE
    )
    titular = models.ForeignKey(
        Titular,
         on_delete=models.PROTECT
    )
    tipo_parientes = models.CharField(
        'Familiar',
        max_length=1,
        choices=tipo_parientes,
        default='P'
    )
    
    def __str__(self):
        return f'{self.username}'

class Administrador(models.Model):
    username = models.OneToOneField(
        Usuario,
        on_delete = models.CASCADE
    ) 
    rol = models.CharField(
        'Cargo',
		max_length=1,
        choices=roles,
        default='G'
	)

    def __str__(self):
        return f'{self.username}'
class Reembolso(models.Model):
    aseguradora = models.ForeignKey(
        Aseguradora,
        on_delete=models.PROTECT
    )
    username = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT
    )
    id = models.IntegerField(
        'Número de factura',
        primary_key=True
    )
    diagnostico = models.CharField(
        'Diagnóstico',
        max_length=255,
        blank=True,
        null=True
    )
    fecha_siniestro = models.DateField(
        'Fecha de siniestro',
        blank=True,
        null=True
    )
    fecha_factura = models.DateField(
        'Fecha de factura',
        blank=False,
        null=False
    )
    concepto = models.CharField(
        'Concepto',
        max_length=255,
        blank=False,
        null=False
    )
    paciente = models.CharField(
        'Paciente',
        max_length=255,
        blank=True,
        null=True
    )
    monto = models.DecimalField(
        'Monto',
        max_digits=10,
        decimal_places=2,
        blank=False,
        null=False
    )
    nroControl = models.CharField(
        'Nro de control',
        max_length=50,
    )
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    ]
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='PENDIENTE'
    )
    cedula_paciente = models.FileField(upload_to='pdfs/reembolso/')
    informe_ampliado = models.FileField(upload_to='pdfs/reembolso/')
    informe_resultado = models.FileField(upload_to='pdfs/reembolso/')
    
    def __str__(self):
        return f'{self.id}'


class CartaAval(models.Model):
    aseguradora = models.ForeignKey(
        Aseguradora,
        on_delete=models.PROTECT
    )
    username = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT
    )
    id = models.IntegerField(
        'Numero de factura',
        primary_key=True
    )
    diagnostico = models.CharField(
        'Diagnostico',
        max_length=255,
        blank=True,  # Ahora no es requerido
        null=True    # Ahora puede ser nulo
    )
    fecha_siniestro = models.DateField(
        'fecha de siniestro',
        blank=True,  # Ahora no es requerido
        null=True    # Ahora puede ser nulo
    )
    fecha_factura = models.DateField(
        'Fecha de factura',
        blank=False,
        null=False
    )
    concepto = models.CharField(
        'Concepto',
        max_length=255,
        blank=False,
        null=False
    )
    paciente = models.CharField(
        'Paciente',
        max_length=255,
        blank=True,  # Ahora no es requerido
        null=True    # Ahora puede ser nulo
    )
    monto = models.DecimalField(
        'Costo',
        max_digits=10,
        decimal_places=2,
        blank=False,
        null=False
    )
    cedula_paciente = models.FileField(upload_to='pdfs/reembolso/')  # Cambia ImageField a FileField
    informe_ampliado = models.FileField(upload_to='pdfs/reembolso/')
    informe_resultado = models.FileField(upload_to='pdfs/reembolso/')
    
    def __str__(self):
        return f'{self.id}'

class SolicitudReembolso(models.Model):
    administrador = models.ForeignKey(
        Administrador,
        on_delete=models.PROTECT
    )
    reembolso = models.ForeignKey(
        Reembolso,
        on_delete=models.PROTECT
    )
    id = models.IntegerField(
        'Numero de siniestro',
        primary_key=True
    )
    estatus = models.CharField(
        'Estatus',
        max_length=1,
        choices=estatus,
        default='P'
    )

    def __str__(self):
        return f'{self.id}'


class SolicitudCartaAval(models.Model):
    administrador = models.ForeignKey(
        Administrador,
        on_delete=models.PROTECT
    )
    carta_aval = models.ForeignKey(
        CartaAval,
        on_delete=models.PROTECT
    )
    id = models.IntegerField(
        'Numero de siniestro',
        primary_key=True
    )
    estatus = models.CharField(
        'Estatus',
        max_length=1,
        choices=estatus,
        default='P'
    )

    def __str__(self):
        return f'{self.id}'