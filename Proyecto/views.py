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


# Create your views here.

#Variables

Usuario = get_user_model()

def homeTitular(request): 
    homeTitularTemplate = open("./Apps/Aplicacion/templates/user/titular/home.html")
    template = Template(homeTitularTemplate.read())
    homeTitularTemplate.close()
    contexto = Context()
    documento = template.render(contexto)
    return HttpResponse(documento)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        #Verificar si el usuario existe
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
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Contraseña inválida'}, status=status.HTTP_401_UNAUTHORIZED)