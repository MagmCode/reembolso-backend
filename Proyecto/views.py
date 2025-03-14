import os
from django.shortcuts import render
from django.http import HttpResponse
import datetime
from django.template import Template, Context
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from django.contrib.staticfiles import finders
from reportlab.lib.enums import TA_CENTER
from django.contrib.auth.models import User
from Apps.Aplicacion.models import Usuario, Aseguradora, Titular
import json
from django.core.exceptions import ValidationError


# VARIABLES GLOBALES

Usuario = get_user_model()

# AUTENTICACIÓN
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # Verificar si el usuario existe
        try:
            user = Usuario.objects.get(username=username)
        except Usuario.DoesNotExist:
            return Response({'error': 'El usuario no existe'}, status=status.HTTP_404_NOT_FOUND)
        
        # Autenticar el usuario
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'is_admin': user.is_staff or user.is_superuser,  # Enviar si es admin
                'rol': user.rol,  # Enviar el rol del usuario
                'username': user.username,  # Enviar el nombre de usuario
                'first_name': user.first_name,  # Enviar el nombre
                'last_name': user.last_name,  # Enviar el apellido
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Contraseña inválida'}, status=status.HTTP_401_UNAUTHORIZED)
        
@csrf_exempt
def logout_view(request):
    logout(request)
    return JsonResponse({'message': 'Logged out successfully'}, status=200)


# REPORTES PDF
# Reporte de reembolsos semanal

def reporte_reembolsos_semanal_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_reembolsos_semanal.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    
    # Parámetros para la tabla y el título
    table_x = 50
    col_widths = [73] * 7      # 7 columnas
    table_width = sum(col_widths)
    
    # --- Dibujar el fondo del título ---
    title_text = "REPORTE DE REEMBOLSOS SEMANAL"
    title_bg_color = colors.HexColor('#d8e7fc')
    title_height = 30
    # Ajusta title_y para que el título aparezca en la posición deseada
    title_y = 725  # Valor modificado para bajar un poco (anteriormente estaba más arriba)
    
    p.setFillColor(title_bg_color)
    p.rect(table_x, title_y, table_width, title_height, fill=True, stroke=False)
    
    # --- Dibujar el título centrado en el rectángulo ---
    title_font = "Helvetica-Bold"
    title_font_size = 16
    p.setFont(title_font, title_font_size)
    p.setFillColor(colors.black)
    text_width = p.stringWidth(title_text, title_font, title_font_size)
    text_x = table_x + (table_width - text_width) / 2
    # Ajusta text_y para centrar verticalmente el texto en el rectángulo
    text_y = title_y + (title_height - title_font_size) / 2 + 4
    p.drawString(text_x, text_y, title_text)
    
    # --- Dibujar la tabla de datos ---
    styles = getSampleStyleSheet()
    header_style = styles["Heading5"]
    header_style.fontSize = 8
    header_style.leading = 10
    header_style.alignment = TA_CENTER  # Encabezados centrados
    
    headers = [
        "Semana", 
        "Año", 
        "Total Reembolsos", 
        "Promedio por día", 
        "Reembolsos Aprobados", 
        "Reembolsos Rechazados", 
        "Reembolsos Pendientes"
    ]
    # Convertir cada encabezado en un Paragraph para que realice el wrap y se centre
    header_row = [Paragraph(f"<b>{h}</b>", header_style) for h in headers]
    
    data_rows = [
        ["15", "2024", "120", "17.14", "105", "10", "5"],
        ["16", "2024", "130", "18.57", "110", "12", "8"],
        # Agrega más filas según sea necesario
    ]
    data = [header_row] + data_rows
    
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#DAE7FB'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4186F4')),
    ]))
    
    # Dibujar la tabla (la posición vertical de la tabla se mantiene igual que antes)
    table.wrapOn(p, table_width, 500)
    table.drawOn(p, table_x, 600)
    
    # --- Dibujar el logo de la empresa (último, para que quede por encima del fondo) ---
    logo_path = finders.find('rest_framework/img/Logo.png')
    if not logo_path or not os.path.exists(logo_path):
        raise Exception(f"No se encontró el logo en la ruta de archivos estáticos: {logo_path}")
    
    # Dibujar el logo; al dibujarlo después, se garantiza que esté por encima
    p.drawImage(logo_path, 40, 700, width=80, height=80, preserveAspectRatio=True)
    
    p.showPage()
    p.save()
    
    return response

# Reporte de reembolsos mensual

def reporte_reembolsos_mensual_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_reembolsos_mensual.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    
    # Parámetros para la tabla y el título
    table_x = 50
    col_widths = [85] * 6      # 6 columnas para el reporte mensual
    table_width = sum(col_widths)  # ancho total de la tabla (~510 pts)
    
    # --- Dibujar el fondo del título ---
    title_text = "REPORTE DE REEMBOLSOS MENSUAL"
    title_bg_color = colors.HexColor('#d8e7fc')  # fondo similar al reporte semanal
    title_height = 30
    title_y = 725  # Ajusta este valor para bajar o subir el título
    
    p.setFillColor(title_bg_color)
    p.rect(table_x, title_y, table_width, title_height, fill=True, stroke=False)
    
    # --- Dibujar el título centrado en el rectángulo ---
    title_font = "Helvetica-Bold"
    title_font_size = 16
    p.setFont(title_font, title_font_size)
    # Para que el título se pinte en negro:
    p.setFillColor(colors.black)
    text_width = p.stringWidth(title_text, title_font, title_font_size)
    text_x = table_x + (table_width - text_width) / 2
    text_y = title_y + (title_height - title_font_size) / 2 + 4
    p.drawString(text_x, text_y, title_text)
    
    # --- Preparar la tabla de datos con encabezados centrados ---
    styles = getSampleStyleSheet()
    header_style = styles["Heading5"]
    header_style.fontSize = 8
    header_style.leading = 10
    header_style.alignment = TA_CENTER  # Encabezados centrados
    
    # Encabezados para el reporte mensual
    headers = [
        "Mes", 
        "Año", 
        "Total Reembolsos", 
        "Promedio Mensual", 
        "Monto Total Reembolsado", 
        "Tiempo Promedio de Procesamiento"
    ]
    header_row = [Paragraph(f"<b>{h}</b>", header_style) for h in headers]
    
    # Datos de ejemplo para el reporte mensual
    data_rows = [
        ["Marzo", "2024", "450", "15", "$50,000", "5 días"],
        ["Abril", "2024", "475", "15.8", "$52,000", "4 días"],
        # Agrega más filas según sea necesario
    ]
    
    data = [header_row] + data_rows
    
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        # Alternar el fondo de las filas (desde la fila 1 en adelante):
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#DAE7FB'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4186F4')),
    ]))
    
    # Dibujar la tabla
    table.wrapOn(p, table_width, 500)
    table.drawOn(p, table_x, 600)
    
    # --- Dibujar el logo de la empresa ---
    logo_path = finders.find('rest_framework/img/Logo.png')
    if not logo_path or not os.path.exists(logo_path):
        raise Exception(f"No se encontró el logo en la ruta de archivos estáticos: {logo_path}")
    
    # Dibujar el logo; al hacerlo al final se asegura que no quede tapado por otros elementos
    p.drawImage(logo_path, 40, 700, width=80, height=80, preserveAspectRatio=True)
    
    p.showPage()
    p.save()
    
    return response

# REGISTRO DE USUARIOS

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validar que la cédula no exista
            if Usuario.objects.filter(username=data['cedula']).exists():
                return JsonResponse({'status': 'error', 'message': 'La cédula ya está registrada'}, status=400)
            
            # Crear el usuario
            user = Usuario.objects.create_user(
                username=data['cedula'],  # Cédula
                password=data['clave'],  # Contraseña
                first_name=data['nombre'],  # Nombre
                last_name=data['apellido'],  # Apellido
                email=data['correo'],  # Correo
                fecha_nacimiento=data['fechaNacimiento'],  # Fecha de nacimiento
                rol='cliente'  # Rol por defecto para nuevos usuarios
            )
            
            # Crear la aseguradora
            aseguradora = Aseguradora.objects.create(
                nombre=data['aseguradora'],
                nro_poliza=data['nroPoliza']
            )
            
            # Crear el titular
            titular = Titular.objects.create(
                username=user,
                aseguradora=aseguradora,
                telefono=data['telefono'],
                telefono_opcional=data.get('telefonoOpcional', None),
                correo=data['correo'],
                vigencia_desde=data['vigenteDesde'],
                vigencia_hasta=data['vigenteHasta']
            )
            
            return JsonResponse({'status': 'success', 'message': 'Usuario registrado correctamente'})
        
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Error en el servidor'}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)