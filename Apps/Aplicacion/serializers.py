from rest_framework import serializers
from .models import Aseguradora, CartaAval, Usuario, Titular, Reembolso

class AseguradoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aseguradora
        fields = ['id', 'nombre']
        
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email']

class TitularProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Titular
        fields = ['telefono', 'telefono_opcional']
        
class ReembolsoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reembolso
        fields = ['id', 'nroControl', 'fecha_factura', 'concepto', 'monto', 
                 'informe_ampliado', 'informe_resultado', 'cedula_paciente',
                 'estado', 'username', 'aseguradora']  # Añadí 'aseguradora'
        extra_kwargs = {
            'username': {'read_only': True},
            'aseguradora': {'read_only': True},
        }
        
class CartaAvalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartaAval
        fields = ['id', 'aseguradora', 'username', 'diagnostico', 'fecha_siniestro', 'fecha_factura', 'concepto', 'paciente', 'monto', 'informe_ampliado', 'informe_resultado', 'cedula_paciente']
        extra_kwargs = {
            'diagnostico': {'required': False, 'allow_null': True},
            'fecha_siniestro': {'required': False, 'allow_null': True},
            'paciente': {'required': False, 'allow_null': True},
        }