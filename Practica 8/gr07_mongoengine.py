from typing_extensions import Required
from mongoengine import connect
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import ReferenceField
connect('giw_mongoengine')

class Usuario(Document):
    dni = StringField(primary_key = True, min_length = 9, max_length = 9, regex = "[0-9]+[A-Z]")
    nombre = StringField(required = True, min_length = 2)
    apellido1 = StringField(required = True, min_length = 2)
    apellido2 = StringField()
    f_nac = DateTimeField(required = True) #mirar como hacer que se adapte al formato
    tarjetas = ListField( EmbeddedDocumentField(Tarjeta) )
    pedidos = ListField( ReferenceField(Pedido) )

    def clean(self):
        #Comprobar que el DNI es válido
        letra = self.dni[8]
        numero = self.dni[0:8]
        letrasResto = "TRWAGMYFPDXBNJZSQVHLCKE"
        resto = numero % 23

        if numero.isdigit() == False: # Compruebo que son números los primeros 8 caracteres
            raise ValidationError("El DNI debe contener 8 números al principio")

        if letra.isdigit() == True: # Compruebo que hay una letra al final
            raise ValidationError("El DNI debe contener 1 letra al final")

        if letrasResto[resto] != letra:# Compruebo que el DNI es válido realizando el cálculo de dígito
            raise ValidationError("El DNI no pasa el cálculo de dígito de control español")


class Tarjeta(EmbeddedDocument):
  nombre = StringField(required = True, min_length = 2)
  numero = IntField(required = True, min_length = 16, max_length = 16)
  mes = IntField(required = True, min_length = 2, max_length = 2, min_value = 1, max_value = 12)
  año = IntField(required = True, min_length = 2, max_length = 2, min_value = 0)
  ccv = IntField(required = True, min_length = 3, max_length = 3, min_value = 0)

class Pedido(Document):
  total = IntField(required = True, min_value = 0)
  fecha = ComplexDateTimeField(required = True)
  lineas = ListField(EmbeddedDocumentField(Linea), required = True)

class Linea(EmbeddedDocument):
  num_items = IntField(required = True, min_value = 0)
  precio_item = FloatField(required = True, min_value = 0)
  nombre_item = StringField(required = True, min_length = 2)
  total = FloatField(required = True, min_value = 0)
  ref = ReferenceField(Producto(), required = True)

class Producto():
  codigo_barras = StringField(required = True, unique = True) #que cumpla el formato del pdf
  nombre = StringField(required = True, min_length = 2)
  categoria_principal = IntField(required = True, min_value = 0)
  categorias_secundarias = IntField(min_value = 0)
