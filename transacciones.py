# Integrantes: Ivanna Correnti y Rodrigo Da Camara
from datetime import datetime


class Venta:
    """Contenedor de datos para registrar una venta realizada.

    Enlaza el producto vendido con el monto cobrado y la tarjeta
    utilizada. No contiene logica de negocio pesada, solo almacena
    la informacion de la transaccion.

    Eficiencia: objeto liviano con atributos primitivos y una
    referencia al producto, sin duplicar datos.
    """

    def __init__(self, producto, monto, hash_tarjeta):
        """Registra los datos de una venta individual.

        Eficiencia: asignacion directa O(1), la marca de tiempo
        se genera una sola vez con datetime.now().
        """
        self.producto = producto
        self.monto = monto
        self.hash_tarjeta = hash_tarjeta
        self.fecha = datetime.now()

    def __str__(self):
        """Devuelve representacion legible de la venta.

        Eficiencia: formateo con f-string, O(1).
        """
        fecha_str = self.fecha.strftime("%d/%m/%Y %H:%M:%S")
        return f"{fecha_str} | {self.producto.nombre} | ${self.monto:.2f} | Tarjeta: {self.hash_tarjeta}"


class Restock:
    """Contenedor de datos para registrar una operacion de restock.

    Enlaza el producto reabastecido con la cantidad agregada.
    No contiene logica de negocio pesada, solo almacena la
    informacion de la reposicion.

    Eficiencia: objeto liviano que registra solo los datos
    esenciales de la operacion de reabastecimiento.
    """

    def __init__(self, producto, cantidad_agregada):
        """Registra los datos de una operacion de restock.

        Eficiencia: asignacion directa O(1), marca de tiempo
        generada una sola vez.
        """
        self.producto = producto
        self.cantidad_agregada = cantidad_agregada
        self.fecha = datetime.now()

    def __str__(self):
        """Devuelve representacion legible del restock.

        Eficiencia: formateo con f-string, O(1).
        """
        fecha_str = self.fecha.strftime("%d/%m/%Y %H:%M:%S")
        return f"{fecha_str} | {self.producto.nombre} | +{self.cantidad_agregada} unidades"
