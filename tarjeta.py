# Integrantes: Ivanna Correnti r R


class Tarjeta:
    """Representa una tarjeta de pago del cliente.

    Mapea los campos del JSON de origen:
        - 'id' -> hash_tarjeta

    Eficiencia: almacena solo dos atributos primitivos,
    ocupando memoria minima por instancia.
    """

    def __init__(self, hash_tarjeta, saldo):
        """Inicializa la tarjeta con su identificador y saldo.

        Eficiencia: asignacion directa O(1) sin transformaciones.
        """
        self.hash_tarjeta = hash_tarjeta
        self.saldo = saldo

    def cobrar(self, monto):
        """Descuenta el monto indicado del saldo de la tarjeta.

        Retorna True si el saldo es suficiente y se realizo el cobro,
        False si el saldo es insuficiente.

        Eficiencia: operacion aritmetica O(1), una comparacion
        y una resta.
        """
        cobro_exitoso = False
        if self.saldo >= monto:
            self.saldo = self.saldo - monto
            cobro_exitoso = True
        return cobro_exitoso

    def __str__(self):
        """Devuelve representacion legible de la tarjeta.

        Eficiencia: formateo con f-string, O(1).
        """
        return f"Tarjeta: {self.hash_tarjeta} | Saldo: ${self.saldo:.2f}"
