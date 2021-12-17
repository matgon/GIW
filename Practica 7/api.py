"""
GIW 2021-22
Práctica 7
Grupo 7
Autores: MATEO GONZALEZ DE MIGUEL, MUAD ROHAIBANI ALKADRI , MARIANA DE LA CARIDAD VILLAR ROJAS, LUIS SÁNCHEZ CAMACHO

(MATEO GONZALEZ DE MIGUEL, MUAD ROHAIBANI ALKADRI , MARIANA DE LA CARIDAD VILLAR ROJAS, LUIS SÁNCHEZ CAMACHO) 
declaramos que esta solución es fruto exclusivamente de nuestro trabajo personal. No hemos sido ayudados por 
ninguna otra persona ni hemos obtenido la solución de fuentes externas, y tampoco hemos compartido nuestra solución
con nadie. Declaramos además que no hemos realizado de manera deshonesta ninguna otra
actividad que pueda mejorar nuestros resultados ni perjudicar los resultados de los demás.
"""
import json
import os
import copy
from flask import Flask, request, session, render_template, Response
app = Flask(__name__)


###
### <DEFINIR AQUI EL SERVICIO REST>
###

asignaturas = list()
id_asignatura = 0

def _check_json(json_body) -> bool:
    if len(json_body) != 3:
        return False
    else:
        try:
            if type(json_body["nombre"]) is not str or type(json_body["numero_alumnos"]) is not int or type(json_body["horario"]) is not list:
                return False
                        
            for h in json_body["horario"]:
                if type(h["dia"]) is not str or type(h["hora_inicio"]) is not int or type(h["hora_final"]) is not int:
                    return False
        except:
            return False
    return True

def _check_campo(json_body: dict):
    if len(json_body) != 1:
        return False
    else:
        for i in json_body:
            campo = str(i)
            break

        print(campo)
        try:
            if campo == "nombre":
                if type(json_body[campo]) is not str:
                    return False
            elif campo == "numero_alumnos":
                if type(json_body[campo]) is not int:
                    return False
            elif campo == "horario":
                if type(json_body[campo]) is not list:
                    return False
                else:
                    for h in json_body[campo]:
                        if type(h["dia"]) is not str or type(h["hora_inicio"]) is not int or type(h["hora_final"]) is not int:
                            return False
            else:
                return False
        except:
            return False
        return campo

def _print_asignaturas(a_list: list) -> list:
    res_list = list()
    for asignatura in a_list:
        res_list.append("/asignaturas/{}".format(asignatura["id"]))
    return res_list

def _split_asignaturas(a_list: list, per_page: int, n_alumnos: int) -> list:
    pag = list()
    pages_list = list()
    c = 0

    for asignatura in a_list:
        if asignatura["numero_alumnos"] >= n_alumnos:
            pag.append(asignatura)
            c += 1
        if c == per_page:
            c = 0
            pages_list.append(pag)
            pag = []
        
    
    if len(pag) > 0:
        pages_list.append(pag)

    return pages_list

##----------------------------------------------------------------------
## 2.1
##----------------------------------------------------------------------
# Invocar la ruta con el metodo delete para vaciar la lista de asginaturas
@app.route('/asignaturas', methods=['DELETE'])
def delete_asignaturas():
    asignaturas.clear()
    global id_asignatura
    id_asignatura = 0
    status_code = Response(status=204)
    return status_code

@app.route('/asignaturas', methods=['POST'])
def create_asignatura():
    global id_asignatura
    request_body = request.json # Obtener el diccionario de la asginatura
    if _check_json(request_body):
        request_body["id"] = id_asignatura
        asignaturas.append(request_body) # Agregar la asignatura
        res = {"id": id_asignatura}
        status_code = Response(response=json.dumps(res), status=201, mimetype='application/json')
        id_asignatura += 1
    else:
        status_code = Response(status=400)

    return status_code

@app.route('/asignaturas', methods=['GET'])
def get_asignaturas():
    page = request.args.get("page")
    per_page = request.args.get("per_page")
    n_alumnos = request.args.get("alumnos_gte")
    global asignaturas
    
    if page is None and per_page is None:  # No hay parametros en la url
        if n_alumnos is None:
            pages_list = _split_asignaturas(asignaturas, len(asignaturas), 0)
        else:
            pages_list = _split_asignaturas(asignaturas, len(asignaturas), int(n_alumnos))
        
        if len(pages_list):
            res_list = _print_asignaturas(pages_list[0])
        else:
            res_list = []
        res = { "asignaturas": res_list }
        
        if len(res_list) == len(asignaturas):
            code = 200
        else: 
            code = 206
            
        status_code = Response(response=json.dumps(res), status=code, mimetype='application/json')

    elif page is not None and int(page) > 0 and per_page is not None and int(per_page) > 0:  # Los dos parametros estan presentes en la url y mayores que 0
        if n_alumnos is None:
            pages_list = _split_asignaturas(asignaturas, int(per_page), 0)
        else:
            pages_list = _split_asignaturas(asignaturas, int(per_page), int(n_alumnos))
        
        if len(pages_list) and int(page)-1 < len(pages_list):
            res_list = _print_asignaturas(pages_list[int(page)-1])
        else: 
            res_list = []
        
        res = { "asignaturas": res_list }
        
        if len(res_list) == len(asignaturas):
            code = 200
        else: 
            code = 206
        
        status_code = Response(response=json.dumps(res), status=code, mimetype='application/json')

    else: # Peticion erronea
        status_code = Response(status=400)


    return status_code

##----------------------------------------------------------------------
## 2.2 
##----------------------------------------------------------------------

@app.route('/asignaturas/<asignatura>', methods=['DELETE'])
def delete_asignatura(asignatura):
    global asignaturas
    encontrado = False

    for a in asignaturas:
        if a["id"] is int(asignatura):
            encontrado = True
            asignaturas.remove(a)
            status_code = Response(status = 204)
            break
    
    if not encontrado: #No existe la asignatura
        status_code = Response(status=404)
            
    return status_code

@app.route('/asignaturas/<asignatura>', methods=['GET'])
def get_asignatura(asignatura):
    global asignaturas
    
    status_code = Response(status=404)
    
    for a in asignaturas:
        if a["id"] is int(asignatura):
            res = a
            status_code = Response(response=json.dumps(res), status=200, mimetype='application/json')
            break        
            
    return status_code

@app.route('/asignaturas/<asignatura>', methods=['PUT'])
def put_asignatura(asignatura):
    global asignaturas
    encontrado = False
    request_body = request.json # Obtener el diccionario de la asginatura
    for a in asignaturas:
        if a["id"] is int(asignatura):
            if _check_json(request_body):
                encontrado = True
                a["nombre"] = request_body["nombre"]
                a["numero_alumnos"] = request_body["numero_alumnos"]
                a["horario"] = request_body["horario"]
                status_code = Response(status=200)
            else:
                encontrado = True
                status_code = Response(status=400)

    if not encontrado:
        status_code = Response(status=404)
            
    return status_code

@app.route('/asignaturas/<asignatura>', methods=['PATCH'])
def patch_asignatura(asignatura):
    global asignaturas
    encontrado = False
    request_body = request.json # Obtener el diccionario de la asginatura
    clave = _check_campo(request_body)
    print(clave)
    if clave:
        for a in asignaturas:
            if a["id"] is int(asignatura):
                encontrado = True
                a[clave] = request_body[clave]                
                status_code = Response(status=200)
    else:
        status_code = Response(status=400)
    if not encontrado:
        status_code = Response(status=404)
            
    return status_code

##----------------------------------------------------------------------
## 2.3
##----------------------------------------------------------------------
@app.route('/asignaturas/<asignatura>/horario', methods=['GET'])
def get_horario(asignatura):
    global asignaturas
    res_list = list()
    
    for a in asignaturas:
        if a["id"] is int(asignatura):
            res_list = a["horario"]
            break
    
    if len(res_list):
        res = { "horario": res_list }
        status_code = Response(response=json.dumps(res), status=200, mimetype='application/json')
    else: # No existe asignatura
        status_code = Response(status=404)
            
    return status_code


class FlaskConfig:
    """Configuración de Flask"""
    # Activa depurador y recarga automáticamente
    ENV = 'development'
    DEBUG = True
    TEST = True
    # Imprescindible para usar sesiones
    SECRET_KEY = "giw2021&!_()"
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
 

if __name__ == '__main__':
    app.config.from_object(FlaskConfig())
    app.run()

