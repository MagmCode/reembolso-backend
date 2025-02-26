# Reembolso-backend

  

Backend del proyecto Automatizacion de reembolsos

  

## Tecnologias

  

- Python3

- Django

  

## Instalacion del entorno virtual

Los entornos virtuales se pueden describir como directorios de instalación aislados. Este aislamiento te permite localizar la instalación de las dependencias de tu proyecto, sin obligarte a instalarlas en todo el sistema.


### Instalación de virtualenv
Para trabajar con un entorno virtual, se debe instalar el paquete de Python virtualenv, una herramienta que se utiliza para crear entornos Python aislados. Crea una carpeta que contiene todos los ejecutables necesarios para usar los paquetes que necesitaría un proyecto de Python.

Nota: Este paso sólo se debe hacer una vez.

```bash
python -m pip install virtualenv
```
Si se presenta el error No module named pip, se ejecuta el siguiente comando:

```bash
python -m ensurepip --upgrade
```

### Creación del entorno
Desde el directorio del proyecto, se accede al directorio src. Luego, se ejecuta el siguiente comando para crear el entorno virtual con el que se va a trabajar.

Nota: Este paso sólo se debe hacer una vez.
```bash
cd src
python -m venv venv
```
### Activación del entorno virtual
Cada vez que se vaya a trabajar en el proyecto, se debe activar el entorno virtual de Python, según el sistema que se esté utilizando.

```bash
venv\Scripts\activate.bat  # En Windows CMD
venv\Scripts\Activate.ps1  # En Windows PowerShell
source venv/Scripts/activate  # En Windows Git Bash
source venv/bin/activate  # En Linux
Instalación de dependencias
```

El proyecto requiere una serie de paquetes para funcionar. Para instalarlos, se usa el siguiente comando:
```bash
python -m pip install -r requirements.txt
```

Desactivación del entorno virtual
Una vez se termine de trabajar en el proyecto, el entorno virtual se puede desactivar con el siguiente comando.
```bash
deactivate
```
  

python -m pip install -r requirements.txt
```
