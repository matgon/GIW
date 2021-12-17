# -*- coding: utf-8 -*-

"""
GIW 2021-22
Práctica 9
Grupo 7
Autores: MATEO GONZALEZ DE MIGUEL, MUAD ROHAIBANI ALKADRI , MARIANA DE LA CARIDAD VILLAR ROJAS, LUIS SÁNCHEZ CAMACHO

(MATEO GONZALEZ DE MIGUEL, MUAD ROHAIBANI ALKADRI , MARIANA DE LA CARIDAD VILLAR ROJAS, LUIS SÁNCHEZ CAMACHO) 
declaramos que esta solución es fruto exclusivamente de nuestro trabajo personal. No hemos sido ayudados por 
ninguna otra persona ni hemos obtenido la solución de fuentes externas, y tampoco hemos compartido nuestra solución
con nadie. Declaramos además que no hemos realizado de manera deshonesta ninguna otra
actividad que pueda mejorar nuestros resultados ni perjudicar los resultados de los demás.
"""


from flask import Flask, request, session, render_template
from flask.wrappers import Response
from mongoengine import connect, Document, StringField, EmailField
# Resto de importaciones
import random
from argon2 import PasswordHasher
from flask_qrcode import QRcode
import pyotp

ph = PasswordHasher()
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ@#$€¬&%"

app = Flask(__name__)
QRcode(app)
connect('giw_auth')


# Clase para almacenar usuarios usando mongoengine
class User(Document):
    user_id = StringField(primary_key=True)
    full_name = StringField(min_length=2, max_length=50, required=True)
    country = StringField(min_length=2, max_length=50, required=True)
    email = EmailField(required=True)
    passwd = StringField(required=True)
    salt = StringField(required=False)
    totp_secret = StringField(required=False)

def _generate_salt() -> str:
    chars=[]
    for i in range(16):
        chars.append(random.choice(ALPHABET))
    
    return ''.join(chars)


##############
# APARTADO 1 #
##############

# 
# Explicación detallada del mecanismo escogido para el almacenamiento de
# contraseñas, explicando razonadamente por qué es seguro
#
"""Se ha empleado argon2 junto con sal añadida para ralentizar y dificultar la obtencion de contraseñas por fuerza bruta"""

@app.route('/signup', methods=['POST'])
def signup():
    nickname = request.form['nickname']
    full_name = request.form['full_name']
    country = request.form['country']
    email = request.form['email']
    password = request.form['password']
    password2 = request.form['password2']
    
    if password != password2:
       res = Response(response="Las contraseñas no coinciden", status=400)
    else:
        try:
            User.objects.get(user_id = nickname)
            res = Response(response="El usuario ya existe", status=400)
        except:
            salt = _generate_salt()
            user = User(user_id = nickname, full_name = full_name, country = country, email = email, passwd = ph.hash(password+salt), salt=salt)
            user.save(cascade=True, force_insert=True)
            res = Response(response=f"Bienvenido usuario {full_name}", status=200)
                        
    return res


@app.route('/change_password', methods=['POST'])
def change_password():
    nickname = request.form['nickname']
    old_password = request.form['old_password']
    new_password = request.form['new_password']
    
    try:
        user = User.objects.get(user_id = nickname)
        if not ph.verify(user.passwd, old_password+user.salt):
            res = Response(response="Usuario o contraseña incorrectos", status=400)
        else:
            salt = _generate_salt()
            user.passwd = ph.hash(new_password+salt)
            user.salt = salt
            user.save() # Update
            res = Response(response=f"La contraseña del usuario {user.user_id} ha sido modificada", status=200)
    except:
        res = Response(response="Usuario o contraseña incorrectos", status=400)
        
    return res
    
 
           
@app.route('/login', methods=['POST'])
def login():
    nickname = request.form['nickname']
    password = request.form['password']
    
    try:
        user = User.objects.get(user_id = nickname)
        if not ph.verify(user.passwd, password+user.salt):
            res = Response(response="Usuario o contraseña incorrectos", status=400)
        else:
            res = Response(response=f"Bienvenido {user.full_name}", status=200)
    except:
        res = Response(response="Usuario o contraseña incorrectos", status=400)
        
    return res
    

##############
# APARTADO 2 #
##############

# 
# Explicación detallada de cómo se genera la semilla aleatoria, cómo se construye
# la URL de registro en Google Authenticator y cómo se genera el código QR
#


@app.route('/signup_totp', methods=['POST'])
def signup_totp():
    nickname = request.form['nickname']
    full_name = request.form['full_name']
    country = request.form['country']
    email = request.form['email']
    password = request.form['password']
    password2 = request.form['password2']
    otp = pyotp.random_base32()
    totp_url = f"otpauth://totp/giw:{email}?secret={otp}&issuer=giw&algorithm=SHA1&digits=6&period=30"
    html = f"""
        <p>Bienvenido usuario {full_name}</p>
        <P>{otp}</p>
        <img src="{{ qrcode({totp_url}) }}">
    """
    
    if password != password2:
       res = Response(response="Las contraseñas no coinciden", status=400)
    else:
        try:
            User.objects.get(user_id = nickname)
            res = Response(response="El usuario ya existe", status=400)
        except:
            salt = _generate_salt()
            user = User(user_id = nickname, full_name = full_name, country = country, email = email, 
                        passwd = ph.hash(password+salt), salt=salt, totp_secret=otp)
            user.save(cascade=True, force_insert=True)
            # res = Response(response=html, status=200)
            res = render_template("signup_display.html", full_name=full_name, otp=otp, totp_url=totp_url)
                        
    return res

@app.route('/login_totp', methods=['POST'])
def login_totp():
    nickname = request.form['nickname']
    password = request.form['password']
    t_otp = request.form['totp']
    
    try:
        user = User.objects.get(user_id = nickname)
        totp = pyotp.TOTP(user.totp_secret)
        if not ph.verify(user.passwd, password+user.salt) or not totp.verify(t_otp):
            res = Response(response="Usuario o contraseña incorrectos", status=400)
        else:
            res = Response(response=f"Bienvenido {user.full_name}", status=200)
    except:
        res = Response(response="Usuario o contraseña incorrectos", status=400)
        
    return res
  

class FlaskConfig:
    """Configuración de Flask"""
    # Activa depurador y recarga automáticamente
    ENV = 'development'
    DEBUG = True
    TEST = True
    # Imprescindible para usar sesiones
    SECRET_KEY = 'la_asignatura_de_giw'
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'


if __name__ == '__main__':
    app.config.from_object(FlaskConfig())
    app.run()
