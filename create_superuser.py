import os
import django

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Proyecto.settings')
django.setup()

from Apps.Aplicacion.models import Usuario

# Verifica si el usuario ya existe
if not Usuario.objects.filter(username='123456').exists():
    # Crea un usuario con el campo 'username' (que almacena la cédula)
    user = Usuario.objects.create_user(
        username='123456',  # Usar 'username' en lugar de 'cedula'
        password='Admin25',  # Contraseña del usuario
        email='admin@example.com',  # Correo electrónico (requerido por REQUIRED_FIELDS)
        first_name='Admin',  # Nombre (requerido por REQUIRED_FIELDS)
        last_name='User',  # Apellido (requerido por REQUIRED_FIELDS)
        fecha_nacimiento='1990-01-01'  # Fecha de nacimiento (requerido por REQUIRED_FIELDS)
    )
    user.is_staff = True  # Hacer que el usuario sea parte del staff
    user.is_superuser = True  # Hacer que el usuario sea un superusuario
    user.save()
    print("Usuario creado exitosamente.")
else:
    print("El usuario ya existe.")