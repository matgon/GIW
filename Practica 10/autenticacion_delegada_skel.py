# -*- coding: utf-8 -*-

#
# CABECERA AQUI
#

from flask import Flask, request, session, Response
import requests, json
import jwt
from urllib import parse

from werkzeug.utils import redirect
# Resto de importaciones


app = Flask(__name__)


# Credenciales. 
# https://developers.google.com/identity/protocols/oauth2/openid-connect#appsetup
# Copiar los valores adecuados.
CLIENT_ID = "799561959123-vpsjjn3chmo2j26b8e8krlo749pp0n40.apps.googleusercontent.com"
CLIENT_SECRET = "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"

REDIRECT_URI = 'http://localhost:5000/token'

# Fichero de descubrimiento para obtener el 'authorization endpoint' y el 
# 'token endpoint'
# https://developers.google.com/identity/protocols/oauth2/openid-connect#authenticatingtheuser
DISCOVERY_DOC = 'https://accounts.google.com/.well-known/openid-configuration'

# token_info endpoint para extraer información de los tokens en depuracion, sin
# descifrar en local
# https://developers.google.com/identity/protocols/OpenIDConnect#validatinganidtoken
TOKENINFO_ENDPOINT = 'https://oauth2.googleapis.com/tokeninfo'

ref=""

@app.route('/login_google', methods=['GET', 'POST'])
def login_google():

    res = requests.request(url = DISCOVERY_DOC, method = "GET").json()

    autorizacion = res["authorization_endpoint"]
    response_type = "response_type=code&client_id="
    client_id = CLIENT_ID + "&"
    scope = "scope=openid%20profile%20email&"
    redirect_uri = "redirect_uri=http://localhost:5000/token"
    
    ref = autorizacion + "?" + response_type + client_id + scope + redirect_uri
    return f"""<a href = {ref}> Pa Google </a>"""

@app.route('/token', methods=['GET', 'POST'])
def token():
    res = requests.request(url = DISCOVERY_DOC, method = "GET").json()
    token_endpoint = res["token_endpoint"]
    code = request.args['code']
    grant_type = 'authorization_code'
    
    url = f'{token_endpoint}?code={code}&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&redirect_uri={REDIRECT_URI}&grant_type={grant_type}'
    res = requests.request(url=url, method='POST').json()
    
    id_token = res['id_token']
    decoded_jwt = jwt.decode(id_token, options={"verify_signature": False})
    email = decoded_jwt['email']
    
    return f"""<p>KLK {email} brrr</p>"""


class FlaskConfig:
    '''Configuración de Flask'''
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
