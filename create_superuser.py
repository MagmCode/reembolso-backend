import os
import django

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Proyecto.settings')
django.setup()

from django.contrib.auth import get_user_model
Usuario = get_user_model()

# Verifica si el usuario ya existe
if not Usuario.objects.filter(username='123456').exists():
    # Crea un usuario con el campo 'username' (que almacena la cédula)
    admin = Usuario.objects.create_user(
        username='123456',  # Cédula
        password='Admin25',  # Contraseña del usuario
        email='admin@example.com',  # Correo electrónico
        first_name='Admin',  # Nombre
        last_name='User',  # Apellido
        fecha_nacimiento='1990-01-01',  # Fecha de nacimiento
        rol='admin'  # Rol de administrador
    )
    admin.is_staff = True  # Hacer que el usuario sea parte del staff
    admin.is_superuser = True  # Hacer que el usuario sea un superusuario
    admin.save()
    print("Usuario creado exitosamente.")
else:
    print("El usuario ya existe.")

USERS = [
    {
        'username': '14920506',
        'password': 'Probando2',
        'email': 'cliente@gmail.com',
        'first_name': 'User',
        'last_name': 'Prueba',
        'fecha_nacimiento': '2003-07-08',
        'rol': 'cliente',  # Rol de cliente
    },
    {
        'username': '29850418',
        'password': 'Analista25',
        'email': 'analista@gmail.com',
        'first_name': 'Analista',
        'last_name': 'Prueba',
        'fecha_nacimiento': '1995-05-15',
        'rol': 'analista',  # Rol de analista
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
            fecha_nacimiento=usuario_data['fecha_nacimiento'],
            rol=usuario_data['rol'],  # Asignar el rol
            is_staff=(usuario_data['rol'] == 'admin'),  # Solo el admin es staff
            is_superuser=(usuario_data['rol'] == 'admin'),  # Solo el admin es superusuario
        )
        usuario.save()
        print(f"Usuario {usuario.username} creado exitosamente.")
    else:
        print(f"El usuario {usuario_data['username']} ya existe.")