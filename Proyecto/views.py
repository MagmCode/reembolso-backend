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
from Apps.Aplicacion.models import CartaAval, SolicitudReembolso, Usuario, Aseguradora, Titular, Reembolso, SolicitudCartaAval
import json
from django.core.exceptions import ValidationError

from Apps.Aplicacion.serializers import AseguradoraSerializer, CartaAvalSerializer, ReembolsoSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
from django.db.models import Q 
from dateutil.relativedelta import relativedelta




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

            # Obtener los datos adicionales del usuario
            try:
                titular = Titular.objects.get(username=user)
                telefono = titular.telefono
                aseguradora = titular.aseguradora.nombre
                nroPoliza = titular.aseguradora.nro_poliza  # Acceder a nro_poliza a través de la relación aseguradora
            except Titular.DoesNotExist:
                telefono = None
                aseguradora = None
                nroPoliza = None

            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'is_admin': user.is_staff or user.is_superuser,  # Enviar si es admin
                'rol': user.rol,  # Enviar el rol del usuario
                'username': user.username,  # Enviar el nombre de usuario
                'first_name': user.first_name,  # Enviar el nombre
                'last_name': user.last_name,  # Enviar el apellido
                'tipo_cedula': user.tipo_cedula,  # Enviar el tipo de cédula
                'telefono': telefono,  # Enviar el teléfono
                'aseguradora': aseguradora,  # Enviar la aseguradora
                'nroPoliza': nroPoliza  # Enviar el número de póliza
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
    
    table_x = 50
    col_widths = [73] * 7      # 7 columnas
    table_width = sum(col_widths)
    
    # --- Dibujar el fondo del título ---
    title_text = "REPORTE DE REEMBOLSOS SEMANAL"
    title_bg_color = colors.HexColor('#d8e7fc')
    title_height = 30
    title_y = 725
    
    p.setFillColor(title_bg_color)
    p.rect(table_x, title_y, table_width, title_height, fill=True, stroke=False)
    
   # --- Dibujar el título centrado en el rectángulo ---
    title_font = "Helvetica-Bold"
    title_font_size = 16
    p.setFont(title_font, title_font_size)
    p.setFillColor(colors.black)
    text_width = p.stringWidth(title_text, title_font, title_font_size)
    text_x = table_x + (table_width - text_width) / 2
    text_y = title_y + (title_height - title_font_size) / 2 + 4
    p.drawString(text_x, text_y, title_text)
    
    # --- Consultar la base de datos para obtener los datos ---
    hoy = datetime.now()
    semanas = []
    for i in range(4):  # Últimas 4 semanas
        inicio_semana = hoy - timedelta(days=hoy.weekday() + 7 * i)
        fin_semana = inicio_semana + timedelta(days=6)
        semanas.append((inicio_semana, fin_semana))
    
    # --- Preparar la tabla de datos con encabezados centrados ---
    styles = getSampleStyleSheet()
    header_style = styles["Heading5"]
    header_style.fontSize = 8
    header_style.leading = 10
    header_style.alignment = TA_CENTER
    
    headers = [
        "Semana", 
        "Año", 
        "Total Reembolsos", 
        "Promedio por día", 
        "Reembolsos Aprobados", 
        "Reembolsos Rechazados", 
        "Reembolsos Pendientes"
    ]
    header_row = [Paragraph(f"<b>{h}</b>", header_style) for h in headers]
    
    # --- Generar las filas de datos desde la base de datos ---
    data_rows = []
    for inicio_semana, fin_semana in semanas:
        reembolsos_semanales = Reembolso.objects.filter(fecha_factura__range=[inicio_semana, fin_semana])
        total_reembolsos = reembolsos_semanales.count()
        reembolsos_aprobados = SolicitudReembolso.objects.filter(reembolso__in=reembolsos_semanales, estatus='A').count()
        reembolsos_rechazados = SolicitudReembolso.objects.filter(reembolso__in=reembolsos_semanales, estatus='R').count()
        reembolsos_pendientes = SolicitudReembolso.objects.filter(reembolso__in=reembolsos_semanales, estatus='P').count()
        promedio_por_dia = total_reembolsos / 7 if total_reembolsos > 0 else 0
        
        data_rows.append([
            str(inicio_semana.isocalendar()[1]),  # Número de la semana
            str(inicio_semana.year),
            str(total_reembolsos),
            f"{promedio_por_dia:.2f}",
            str(reembolsos_aprobados),
            str(reembolsos_rechazados),
            str(reembolsos_pendientes),
        ])
    
    data = [header_row] + data_rows
    
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#DAE7FB'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4186F4')),
    ]))
    
    # Dibujar la tabla
    table.wrapOn(p, table_width, 500)
    table.drawOn(p, table_x, 550)
    
    # --- Dibujar el logo de la empresa ---
    logo_path = finders.find('rest_framework/img/Logo.png')
    if not logo_path or not os.path.exists(logo_path):
        raise Exception(f"No se encontró el logo en la ruta de archivos estáticos: {logo_path}")
    
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
    col_widths = [85] * 6  # 6 columnas para el reporte mensual
    table_width = sum(col_widths)
    
    # --- Dibujar el fondo del título ---
    title_text = "REPORTE DE REEMBOLSOS MENSUAL"
    title_bg_color = colors.HexColor('#d8e7fc')
    title_height = 30
    title_y = 725
    
    p.setFillColor(title_bg_color)
    p.rect(table_x, title_y, table_width, title_height, fill=True, stroke=False)
    
    # --- Dibujar el título centrado en el rectángulo ---
    title_font = "Helvetica-Bold"
    title_font_size = 16
    p.setFont(title_font, title_font_size)
    p.setFillColor(colors.black)
    text_width = p.stringWidth(title_text, title_font, title_font_size)
    text_x = table_x + (table_width - text_width) / 2
    text_y = title_y + (title_height - title_font_size) / 2 + 4
    p.drawString(text_x, text_y, title_text)
    
    # --- Consultar la base de datos para obtener los datos ---
    hoy = datetime.now()
    meses = []
    for i in range(6):  # Últimos 6 meses
        inicio_mes = hoy.replace(day=1) - relativedelta(months=i)  # Restar meses usando relativedelta
        fin_mes = inicio_mes + relativedelta(day=31)  # Último día del mes
        meses.append((inicio_mes, fin_mes))
    
    # --- Preparar la tabla de datos con encabezados centrados ---
    styles = getSampleStyleSheet()
    header_style = styles["Heading5"]
    header_style.fontSize = 8
    header_style.leading = 10
    header_style.alignment = TA_CENTER
    
    headers = [
        "Mes", 
        "Año", 
        "Total Reembolsos", 
        "Promedio Mensual", 
        "Monto Total Reembolsado", 
        "Tiempo Promedio de Procesamiento"
    ]
    header_row = [Paragraph(f"<b>{h}</b>", header_style) for h in headers]
    
    # --- Generar las filas de datos desde la base de datos ---
    data_rows = []
    for inicio_mes, fin_mes in meses:
        reembolsos_mensuales = Reembolso.objects.filter(fecha_factura__range=[inicio_mes, fin_mes])
        total_reembolsos = reembolsos_mensuales.count()
        monto_total_reembolsado = sum(reembolso.monto for reembolso in reembolsos_mensuales)
        
        # Calcular el tiempo promedio de procesamiento solo para reembolsos con fecha_siniestro no nula
        reembolsos_validos = [reembolso for reembolso in reembolsos_mensuales if reembolso.fecha_siniestro is not None]
        tiempo_total_procesamiento = sum((reembolso.fecha_factura - reembolso.fecha_siniestro).days for reembolso in reembolsos_validos)
        tiempo_promedio_procesamiento = tiempo_total_procesamiento / len(reembolsos_validos) if len(reembolsos_validos) > 0 else 0
        
        data_rows.append([
            inicio_mes.strftime("%B"),  # Nombre del mes
            str(inicio_mes.year),
            str(total_reembolsos),
            f"{total_reembolsos / 30:.2f}",  # Promedio diario
            f"${monto_total_reembolsado:,.2f}",
            f"{tiempo_promedio_procesamiento:.2f} días",
        ])
    
    data = [header_row] + data_rows
    
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#DAE7FB'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4186F4')),
    ]))
    
    # Dibujar la tabla
    table.wrapOn(p, table_width, 500)
    table.drawOn(p, table_x, 525)  # Ajusta la posición vertical de la tabla
    
    # --- Dibujar el logo de la empresa ---
    logo_path = finders.find('rest_framework/img/Logo.png')
    if not logo_path or not os.path.exists(logo_path):
        raise Exception(f"No se encontró el logo en la ruta de archivos estáticos: {logo_path}")
    
    p.drawImage(logo_path, 40, 700, width=80, height=80, preserveAspectRatio=True)
    
    p.showPage()
    p.save()
    
    return response



# REPORTES CARTA AVAL SEMANAL

def reporte_cartas_aval_semanal_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_cartas_aval_semanal.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    
    # Parámetros para la tabla y el título
    table_x = 50
    col_widths = [73] * 7  # 7 columnas
    table_width = sum(col_widths)
    
    # --- Dibujar el fondo del título ---
    title_text = "REPORTE DE CARTAS AVAL SEMANAL"
    title_bg_color = colors.HexColor('#d8e7fc')
    title_height = 30
    title_y = 725
    
    p.setFillColor(title_bg_color)
    p.rect(table_x, title_y, table_width, title_height, fill=True, stroke=False)
    
    # --- Dibujar el título centrado en el rectángulo ---
    title_font = "Helvetica-Bold"
    title_font_size = 16
    p.setFont(title_font, title_font_size)
    p.setFillColor(colors.black)
    text_width = p.stringWidth(title_text, title_font, title_font_size)
    text_x = table_x + (table_width - text_width) / 2
    text_y = title_y + (title_height - title_font_size) / 2 + 4
    p.drawString(text_x, text_y, title_text)
    
    # --- Consultar la base de datos para obtener los datos ---
    hoy = datetime.now()
    semanas = []
    for i in range(4):  # Últimas 4 semanas
        inicio_semana = hoy - timedelta(days=hoy.weekday() + 7 * i)
        fin_semana = inicio_semana + timedelta(days=6)
        semanas.append((inicio_semana, fin_semana))
    
    # --- Preparar la tabla de datos con encabezados centrados ---
    styles = getSampleStyleSheet()
    header_style = styles["Heading5"]
    header_style.fontSize = 8
    header_style.leading = 10
    header_style.alignment = TA_CENTER
    
    headers = [
        "Semana", 
        "Año", 
        "Total Cartas Aval", 
        "Promedio por día", 
        "Cartas Aval Aprobadas", 
        "Cartas Aval Rechazadas", 
        "Cartas Aval Pendientes"
    ]
    header_row = [Paragraph(f"<b>{h}</b>", header_style) for h in headers]
    
    # --- Generar las filas de datos desde la base de datos ---
    data_rows = []
    for inicio_semana, fin_semana in semanas:
        cartas_aval_semanales = CartaAval.objects.filter(fecha_factura__range=[inicio_semana, fin_semana])
        total_cartas_aval = cartas_aval_semanales.count()
        cartas_aval_aprobadas = SolicitudCartaAval.objects.filter(carta_aval__in=cartas_aval_semanales, estatus='A').count()
        cartas_aval_rechazadas = SolicitudCartaAval.objects.filter(carta_aval__in=cartas_aval_semanales, estatus='R').count()
        cartas_aval_pendientes = SolicitudCartaAval.objects.filter(carta_aval__in=cartas_aval_semanales, estatus='P').count()
        promedio_por_dia = total_cartas_aval / 7 if total_cartas_aval > 0 else 0
        
        data_rows.append([
            str(inicio_semana.isocalendar()[1]),  # Número de la semana
            str(inicio_semana.year),
            str(total_cartas_aval),
            f"{promedio_por_dia:.2f}",
            str(cartas_aval_aprobadas),
            str(cartas_aval_rechazadas),
            str(cartas_aval_pendientes),
        ])
    
    data = [header_row] + data_rows
    
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#DAE7FB'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4186F4')),
    ]))
    
    # Dibujar la tabla
    table.wrapOn(p, table_width, 500)
    table.drawOn(p, table_x, 550)
    
    # --- Dibujar el logo de la empresa ---
    logo_path = finders.find('rest_framework/img/Logo.png')
    if not logo_path or not os.path.exists(logo_path):
        raise Exception(f"No se encontró el logo en la ruta de archivos estáticos: {logo_path}")
    
    p.drawImage(logo_path, 40, 700, width=80, height=80, preserveAspectRatio=True)
    
    p.showPage()
    p.save()
    
    return response

# CARTA AVAL MENSUAL

def reporte_cartas_aval_mensual_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_cartas_aval_mensual.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    
    # Parámetros para la tabla y el título
    table_x = 50
    col_widths = [85] * 6  # 6 columnas para el reporte mensual
    table_width = sum(col_widths)
    
    # --- Dibujar el fondo del título ---
    title_text = "REPORTE DE CARTAS AVAL MENSUAL"
    title_bg_color = colors.HexColor('#d8e7fc')
    title_height = 30
    title_y = 725
    
    p.setFillColor(title_bg_color)
    p.rect(table_x, title_y, table_width, title_height, fill=True, stroke=False)
    
    # --- Dibujar el título centrado en el rectángulo ---
    title_font = "Helvetica-Bold"
    title_font_size = 16
    p.setFont(title_font, title_font_size)
    p.setFillColor(colors.black)
    text_width = p.stringWidth(title_text, title_font, title_font_size)
    text_x = table_x + (table_width - text_width) / 2
    text_y = title_y + (title_height - title_font_size) / 2 + 4
    p.drawString(text_x, text_y, title_text)
    
    # --- Consultar la base de datos para obtener los datos ---
    hoy = datetime.now()
    meses = []
    for i in range(6):  # Últimos 6 meses
        inicio_mes = hoy.replace(day=1) - relativedelta(months=i)  # Restar meses usando relativedelta
        fin_mes = inicio_mes + relativedelta(day=31)  # Último día del mes
        meses.append((inicio_mes, fin_mes))
    
    # --- Preparar la tabla de datos con encabezados centrados ---
    styles = getSampleStyleSheet()
    header_style = styles["Heading5"]
    header_style.fontSize = 8
    header_style.leading = 10
    header_style.alignment = TA_CENTER
    
    headers = [
        "Mes", 
        "Año", 
        "Total Cartas Aval", 
        "Promedio Mensual", 
        "Monto Total Avalado", 
        "Tiempo Promedio de Procesamiento"
    ]
    header_row = [Paragraph(f"<b>{h}</b>", header_style) for h in headers]
    
    # --- Generar las filas de datos desde la base de datos ---
    data_rows = []
    for inicio_mes, fin_mes in meses:
        cartas_aval_mensuales = CartaAval.objects.filter(fecha_factura__range=[inicio_mes, fin_mes])
        total_cartas_aval = cartas_aval_mensuales.count()
        monto_total_avalado = sum(carta_aval.monto for carta_aval in cartas_aval_mensuales)
        
        # Calcular el tiempo promedio de procesamiento solo para cartas aval con fecha_siniestro no nula
        cartas_aval_validas = [carta_aval for carta_aval in cartas_aval_mensuales if carta_aval.fecha_siniestro is not None]
        tiempo_total_procesamiento = sum((carta_aval.fecha_factura - carta_aval.fecha_siniestro).days for carta_aval in cartas_aval_validas)
        tiempo_promedio_procesamiento = tiempo_total_procesamiento / len(cartas_aval_validas) if len(cartas_aval_validas) > 0 else 0
        
        data_rows.append([
            inicio_mes.strftime("%B"),  # Nombre del mes
            str(inicio_mes.year),
            str(total_cartas_aval),
            f"{total_cartas_aval / 30:.2f}",  # Promedio diario
            f"${monto_total_avalado:,.2f}",
            f"{tiempo_promedio_procesamiento:.2f} días",
        ])
    
    data = [header_row] + data_rows
    
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#DAE7FB'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4186F4')),
    ]))
    
    # Dibujar la tabla
    table.wrapOn(p, table_width, 500)
    table.drawOn(p, table_x, 525)  # Ajusta la posición vertical de la tabla
    
    # --- Dibujar el logo de la empresa ---
    logo_path = finders.find('rest_framework/img/Logo.png')
    if not logo_path or not os.path.exists(logo_path):
        raise Exception(f"No se encontró el logo en la ruta de archivos estáticos: {logo_path}")
    
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
            if Usuario.objects.filter(username=data.get('cedula')).exists():
                return JsonResponse({'status': 'error', 'message': 'La cédula ya está registrada'}, status=400)
            
            # Validar campos requeridos
            required_fields = [
                'cedula', 'clave', 'nombre', 'apellido', 'correo',
                'fechaNacimiento', 'aseguradora', 'nroPoliza', 'telefono',
                'vigenteDesde', 'vigenteHasta'
            ]
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'status': 'error', 'message': f'Falta el campo requerido: {field}'}, status=400)
            
            # Crear el usuario (solo el número de cédula en username)
            user = Usuario.objects.create_user(
                username=data['cedula'],  # Solo el número de cédula
                password=data['clave'],  # Contraseña
                first_name=data['nombre'],  # Nombre
                last_name=data['apellido'],  # Apellido
                email=data['correo'],  # Correo
                fecha_nacimiento=data['fechaNacimiento'],  # Fecha de nacimiento
                rol='cliente',  # Rol por defecto para nuevos usuarios
                tipo_cedula=data['tipoCedula']  # Guardar el tipo de cédula (V o E)
            )
            
            # Crear la aseguradora
            aseguradora = Aseguradora.objects.create(
                nombre=data['aseguradora'],
                nro_poliza=data['nroPoliza']
            )
            
            # Manejar telefonoOpcional
            telefono_opcional = data.get('telefonoOpcional')
            if telefono_opcional == '' or telefono_opcional is None:
                telefono_opcional = None  # Enviar como null si está vacío o es null
            else:
                telefono_opcional = int(telefono_opcional)  # Convertir a número si tiene valor
            
            # Crear el titular
            titular = Titular.objects.create(
                username=user,
                aseguradora=aseguradora,
                telefono=data['telefono'],
                telefono_opcional=telefono_opcional,  # Puede ser null
                correo=data['correo'],
                vigencia_desde=data['vigenteDesde'],
                vigencia_hasta=data['vigenteHasta']
            )
            
            return JsonResponse({'status': 'success', 'message': 'Usuario registrado correctamente'})
        
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error en el servidor: {str(e)}'}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


# LISTA DE ASEGURADORAS

class AseguradoraList(generics.ListAPIView):
    queryset = Aseguradora.objects.all()
    serializer_class = AseguradoraSerializer
    

# FORGOT PASSWORD

@csrf_exempt
def validate_cedula_email(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('cedula')  # Cambiar 'cedula' por 'username'
            email = data.get('email')

            if not username or not email:
                return JsonResponse({'valid': False, 'error': 'Cédula y email son requeridos'}, status=400)

            # Verificar si el usuario existe
            user = Usuario.objects.get(username=username)
            
            # Verificar si el correo coincide
            if user.email != email:
                return JsonResponse({'valid': False, 'error': 'Correo incorrecto'}, status=400)
            
            return JsonResponse({'valid': True})
        except Usuario.DoesNotExist:
            return JsonResponse({'valid': False, 'error': 'Usuario no registrado'}, status=400)
        except Exception as e:
            # Capturar cualquier otra excepción
            return JsonResponse({'valid': False, 'error': str(e)}, status=500)
    else:
        # Si el método no es POST, devolver un error 405 (Método no permitido)
        return JsonResponse({'error': 'Método no permitido'}, status=405)
        
        
# UPDATE PASSWORD

@csrf_exempt
def update_password(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('cedula')  # Mantener 'cedula' como clave
            current_password = data.get('currentPassword')  # Nuevo campo para cambio normal
            new_password = data.get('newPassword')

            if not username or not new_password:
                return JsonResponse({'success': False, 'error': 'Cédula y nueva contraseña son requeridos'}, status=400)

            # Verificar si el usuario existe
            user = Usuario.objects.get(username=username)

            # Si se proporciona la contraseña actual, validarla (para cambio normal)
            if current_password:
                if not user.check_password(current_password):
                    return JsonResponse({'success': False, 'error': 'Contraseña actual incorrecta'}, status=400)

            # Validar que la nueva contraseña no sea igual a la actual
            if user.check_password(new_password):
                return JsonResponse({'success': False, 'error': 'La nueva contraseña no puede ser igual a la actual'}, status=400)

            # Actualizar la contraseña
            user.set_password(new_password)
            user.save()
            return JsonResponse({'success': True, 'message': 'Contraseña actualizada correctamente'})
        except Usuario.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Usuario no encontrado'}, status=400)
        except Exception as e:
            # Capturar cualquier otra excepción
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        # Si el método no es POST, devolver un error 405 (Método no permitido)
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    
    # EDITT PROFILE
    
class UserProfileView(APIView):
    def get(self, request):
        user = request.user
        try:
            titular = Titular.objects.get(username=user)
            data = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'telefono': titular.telefono,
                'telefono_opcional': titular.telefono_opcional,
            }
            return Response(data, status=status.HTTP_200_OK)
        except Titular.DoesNotExist:
            return Response({'error': 'Titular no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        user = request.user
        try:
            titular = Titular.objects.get(username=user)
            user.first_name = request.data.get('first_name', user.first_name)
            user.last_name = request.data.get('last_name', user.last_name)
            user.email = request.data.get('email', user.email)
            user.save()

            titular.telefono = request.data.get('telefono', titular.telefono)
            titular.telefono_opcional = request.data.get('telefono_opcional', titular.telefono_opcional)
            titular.save()

            return Response({'message': 'Perfil actualizado correctamente'}, status=status.HTTP_200_OK)
        except Titular.DoesNotExist:
            return Response({'error': 'Titular no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
# REEMBOLSO CLIENTE

class ReembolsoListCreateView(generics.ListCreateAPIView):
    serializer_class = ReembolsoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reembolso.objects.filter(username=self.request.user)

    def perform_create(self, serializer):
        # Obtener la aseguradora del titular automáticamente
        titular = Titular.objects.get(username=self.request.user)
        
        serializer.save(
            username=self.request.user,
            aseguradora=titular.aseguradora,
            estado='En revisión'  # Valor por defecto
        )
        
        
# CARTA AVAL CLIENTE
class CartaAvalListCreateView(generics.ListCreateAPIView):
    serializer_class = CartaAvalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filtrar las cartas aval del usuario actual.
        return CartaAval.objects.filter(username=self.request.user)

    def perform_create(self, serializer):
        # Asignar automáticamente el usuario actual a la carta aval creada.
        serializer.save(username=self.request.user)
        