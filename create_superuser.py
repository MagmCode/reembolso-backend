import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto.settings')
django.setup()

from  Apps.Aplicacion.models import Usuario

# Verifica si el usuario ya existe
if not Usuario.objects.filter(cedula='1234567890').exists():
    user = Usuario.objects.create_user(cedula='1234567890', password='password123')
    user.is_staff = True  # Si necesitas que sea un superusuario
    user.is_superuser = True
    user.save()
    print("Usuario creado exitosamente.")
else:
    print("El usuario ya existe.")