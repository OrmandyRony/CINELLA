__author__ = 'Rony Ortiz Alvarez'

from flask import Flask, request, render_template, session, redirect, url_for
import json
import os.path
from time import time
from os import listdir

app = Flask(__name__)

root = os.path.realpath(os.path.dirname(__file__))

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    """ 
    Procesa las urls. '/' y '/index'.
    :return: contenido del archivo index.html 
    """
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    """
    Procesa la url '/login'(formulario para iniciar sesión en el sistema)
    :return: en primer lugar, mostrara la pagina para completar los datos 
    de inicio de sesion. Posteriormente procesara estos datos.
    """
    if request.method == 'POST':
        faltan = []
        campos = ['usuario', 'contrasena', 'ingresar']
        for campo in campos:
            valor = request.form.get(campo, None)
            if valor is None or valor == '':
                faltan.append(campo)
        if faltan:
            return render_template("camposFaltantes.html", datos=faltan, next=url_for("login"))
        return ingresar_usuario(request.form['usuario'], request.form['contrasena'])
 
    return app.send_static_file('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        return registrarse()

    return app.send_static_file('signup.html')

@app.route('/inicio', methods=['GET', 'POST'])
def inicio():
    """
    Procesa la url '/inicio'(página principal de la aplicación)
    :return: inicio.html
    """
    if 'nombre' not in session:
        return "Usted no a ingresado"
    if request.method == 'POST' and request.form['mensaje'] != "":
        mensajes = session['mensajes']
        if not mensajes:
            mensajes = []
        mensajes.append((time(), request.form['mensaje']))
    else:
        mensajes = session['mensajes']
    session['mensajes'] = mensajes
    return render_template('inicio.html')

def registrarse():
    faltan = []
    campos = ['nombre','apellido','usuario','contrasena','confirmar', 'registrarse']
    for campo in campos:
        value = request.form.get(campo, None)
        if value is None or value == '':
            faltan.append(campo)
    if faltan:
        return render_template("camposFaltantes.html", datos=faltan, next=url_for("signup"))
    return crear_usuario(request.form['nombre'], request.form['apellido'], request.form['usuario'], request.form['contrasena'], request.form['confirmar'])

def crear_usuario(nombre, apellido, usuario, contrasena, confirmar):
    """
    Crea un archivo(en la carpeta/data) para almacenar los datos del susario.
    El nombre del archivo coincidira con el nombre del usuario.
    Si el archivo ya existe devueve error.
    Si la contraseña no coincide con la confirmación, devuelve un error.
    :parametro name:  nombre del usuario
    :parametro apellido: apellido del usuario,que luego  utilizara para recuperar 
    datos
    :parametro contrasena: contraseña para futuros inicio de sesión
    :parametro confirmar: confirmacion, debe coincidir con la contraseña
    :return: si no se encuentra ningún error, se envía al usuario a la página de 
    inicio
    """
    directorio = os.path.join(root, "data")
    if not os.path.exists(directorio):
        os.makedirs(directorio)
    file_path = os.path.join(root, "data/", usuario)
    if os.path.isfile(file_path):
        return "Error ya existe un usuario con ese nombre"
    if contrasena != confirmar:
        return "Las contraseñas no son iguales"
    
    datos = {
        "nombre": nombre,
        "apellido": apellido,
        "contrasena": contrasena,
        "mensajes": [],
        "peliculas": []
    }

    with open(file_path, 'w') as f:
        json.dump(datos, f)
    session['nombre'] = nombre
    session['contraseña'] = contrasena
    session['mensages'] = []
    session['usuario'] = usuario
    return redirect(url_for("index"))

def ingresar_usuario(usuario, contrasena):
    """
    Carga los datos para el usuario dado(identificado por el nombre de usuario)
    desde el  directorio data.
    Busca un archivo cuyo nombre coincida con el nombre de usuario.
    :parametro usuario: id usuario
    :parametro contrasena: contraseña a verficar para validar al usuario
    :return: contenido de la página de inicio, si el usuario existe y lacontraseña es correcta.
    """
    file_path = os.path.join(root, "data/", usuario)
    if not os.path.isfile(file_path):
        return "El nombre del usuario no existe"
    with open(file_path, 'r') as f:
        data = json.load(f)
    if data['contrasena'] != contrasena:
        return "La contraseña no es valida"
    session['nombre'] = data['nombre']
    session['apellido'] = data['apellido']
    session['contrasena'] = contrasena
    session['usuario'] = usuario
    session['mensajes'] = data['mensajes']
    session['peliculas'] = data['peliculas']
    return redirect(url_for("inicio"))

app.secret_key = 'amo_sistemas'

if __name__ == '__main__':
    app.run(debug=True, port=5000)