# Integrantes: Ivanna Correnti r R


class Producto:
    """Representa un producto dentro de la maquina expendedora.

    Mapea los campos del JSON de origen:
        - 'cod'  -> codigo
        - 'prod' -> nombre

    Eficiencia: se usa acceso directo a atributos O(1) en lugar
    de estructuras de busqueda adicionales.
    """

    def __init__(self, coordenada, codigo, nombre, precio, cantidad, despedida):
        """Inicializa un producto con todos sus atributos.

        Eficiencia: asignacion directa de atributos sin validaciones
        costosas en tiempo de construccion; la validacion se delega
        al punto de uso para evitar overhead innecesario.
        """
        self.coordenada = coordenada
        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio
        self.cantidad = cantidad
        self.despedida = despedida

    def reducir_cantidad(self, cant):
        """Reduce el stock del producto en la cantidad indicada.

        Retorna True si la operacion fue exitosa, False si el stock
        es insuficiente.

        Eficiencia: operacion O(1), solo una comparacion y una resta.
        """
        exito = False
        if self.cantidad >= cant:
            self.cantidad = self.cantidad - cant
            exito = True
        return exito

    def __str__(self):
        """Devuelve representacion legible del producto.

        Eficiencia: formateo simple con f-string, O(1).
        """
        return f"{self.coordenada} | {self.codigo} | {self.nombre} | ${self.precio:.2f} | Stock: {self.cantidad}"
