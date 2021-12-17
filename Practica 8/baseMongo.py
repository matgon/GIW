from mongoengine import connect
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
        numero = self.dni[:-1]
        letrasResto = "TRWAGMYFPDXBNJZSQVHLCKE"
        resto = numero % 23

        if numero.isdigit() == False: # Compruebo que son números los primeros 8 caracteres
            raise ValidationError("El DNI debe contener 8 números al principio")

        if letra.isdigit() == True: # Compruebo que hay una letra al final
            raise ValidationError("El DNI debe contener 1 letra al final")

        if letrasResto[resto] != letra:# Compruebo que el DNI es válido realizando el cálculo de dígito
            raise ValidationError("El DNI no pasa el cálculo de dígito de control español")


class Tarjeta(EmbeddedDocument):



class Pedido(Document):