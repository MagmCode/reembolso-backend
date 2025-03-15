from rest_framework import serializers
from .models import Aseguradora

class AseguradoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aseguradora
        fields = ['id', 'nombre']