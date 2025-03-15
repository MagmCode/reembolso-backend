
from django import views
from django.contrib import admin
from django.urls import path
# from Proyecto.views import homeTitular
from .views import LoginView, logout_view, reporte_reembolsos_mensual_pdf, reporte_reembolsos_semanal_pdf, register_user, AseguradoraList, validate_cedula_email, update_password
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('home/', homeTitular),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', logout_view, name='logout'),
    path('reporte-reembolsos-semanal/', reporte_reembolsos_semanal_pdf, name='reporte_reembolsos_semanal'),
    path('reporte-reembolsos-mensual/', reporte_reembolsos_mensual_pdf, name='reporte_reembolsos_mensual'),
    path('api/register/', register_user, name='register_user'),
    path('api/aseguradoras/', AseguradoraList.as_view(), name='aseguradora-list'),
    path('api/validate-cedula-email/', validate_cedula_email, name='validate_cedula_email'),
    path('api/update-password/', update_password, name='update_password'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)