
from django import views
from django.contrib import admin
from django.urls import path
# from Proyecto.views import homeTitular
from .views import CartaAvalListCreateView, LoginView, ReembolsoListCreateView, logout_view, reporte_cartas_aval_mensual_pdf, reporte_cartas_aval_semanal_pdf, reporte_reembolsos_mensual_pdf, reporte_reembolsos_semanal_pdf, register_user, AseguradoraList, validate_cedula_email, update_password, UserProfileView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('home/', homeTitular),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', logout_view, name='logout'),
    path('reporte-reembolsos-semanal/', reporte_reembolsos_semanal_pdf, name='reporte_reembolsos_semanal'),
    path('reporte-reembolsos-mensual/', reporte_reembolsos_mensual_pdf, name='reporte_reembolsos_mensual'),
    path('reporte-cartas-aval-semanal/', reporte_cartas_aval_semanal_pdf, name='reporte_cartas_aval_semanal'),
    path('reporte-cartas-aval-mensual/', reporte_cartas_aval_mensual_pdf, name='reporte_cartas_aval_mensual'),
    path('api/register/', register_user, name='register_user'),
    path('api/aseguradoras/', AseguradoraList.as_view(), name='aseguradora-list'),
    path('api/validate-cedula-email/', validate_cedula_email, name='validate_cedula_email'),
    path('api/update-password/', update_password, name='update_password'),
    path('api/user-profile/', UserProfileView.as_view(), name='user-profile'),
     path('api/reembolsos/', ReembolsoListCreateView.as_view(), name='reembolso-list-create'),
     path('api/cartaaval/', CartaAvalListCreateView.as_view(), name='carta-aval-list-create'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)