from django.shortcuts import render
from django.http import HttpResponse
import datetime
from django.template import Template, Context

# Create your views here.
def homeTitular(request): 
    homeTitularTemplate = open("/Apps/templates/user/titular/home.html")
    template = Template(homeTitularTemplate.read())
    homeTitularTemplate.close()
    contexto = Context()
    documento = template.render(contexto)
    return HttpResponse(documento)