from django import forms
from .models import Reembolso, CartaAval

class ReembolsoImagenForman(forms.ModelForm):
    class Meta:
        model = Reembolso
        fields = [
            'id',
            'diagnostico',
            'fecha_siniestro',
            'fecha_factura',
            'concepto',
            'paciente',
            'monto',
            'informe_ampliado',
            'informe_resultado',
            'aseguradora',
            'username'
        ]

class CartaAvalImagenForman(forms.ModelForm):
    class Meta:
        model = CartaAval
        fields = [
            'id',
            'fecha_siniestro',
            'fecha_registro',
            'diagnostico',
            'procedimiento',
            'clinica',
            'monto',
            'paciente',
            'informe_resultado',
            'informe_ampliado'
            'aseguradora',
            'username'
        ]