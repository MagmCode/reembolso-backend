import os
import django

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Proyecto.settings')
django.setup()

# from Apps.Aplicacion.models import Usuario
from django.contrib.auth import get_user_model
Usuario = get_user_model()

# Verifica si el usuario ya existe
if not Usuario.objects.filter(username='123456').exists():
    # Crea un usuario con el campo 'username' (que almacena la cédula)
    admin = Usuario.objects.create_user(
        username='123456',  # Usar 'username' en lugar de 'cedula'
        password='Admin25',  # Contraseña del usuario
        email='admin@example.com',  # Correo electrónico (requerido por REQUIRED_FIELDS)
        first_name='Admin',  # Nombre (requerido por REQUIRED_FIELDS)
        last_name='User',  # Apellido (requerido por REQUIRED_FIELDS)
        fecha_nacimiento='1990-01-01'  # Fecha de nacimiento (requerido por REQUIRED_FIELDS)
    )
    admin.is_staff = True  # Hacer que el usuario sea parte del staff
    admin.is_superuser = True  # Hacer que el usuario sea un superusuario
    admin.save()
    print("Usuario creado exitosamente.")
else:
    print("El usuario ya existe.")

USERS = [
    {
        'username': '29850418',
        'password': 'Admin2503',
        'email': 'maria@gmail.com',
        'first_name': 'Maria',
        'last_name': 'Mendoza',
        'fecha_nacimiento': '2003-07-08',
    },
]

for usuario_data in USERS:
    if not Usuario.objects.filter(username=usuario_data['username']).exists():
        usuario = Usuario.objects.create_user(
            username=usuario_data['username'],
            password=usuario_data['password'],
            email=usuario_data['email'],
            first_name=usuario_data['first_name'],
            last_name=usuario_data['last_name'],
            fecha_nacimiento=['fecha_nacimiento'],
            is_staff=False,
            is_superuser=False,
        )
        usuario.save()
        print(f"Usuario {usuario.username} creado exitosamente.")
    else:
        print(f"El usuario {usuario_data['username']} ya existe.")