# Integrantes: Ivanna Correnti y Rodrigo Da Camara
from producto import Producto


class Inventario:
    """Administra la coleccion de productos de la maquina expendedora.

    Mantiene una lista interna de objetos Producto y expone metodos
    de busqueda sin imprimir directamente; delega la presentacion
    a la capa de la maquina.

    Eficiencia: las busquedas recorren la lista en O(n) donde n es
    la cantidad de productos. Para el volumen tipico de una maquina
    expendedora (< 100 productos), esto es optimo sin necesidad de
    indices adicionales.
    """

    def __init__(self):
        """Inicializa el inventario con una lista vacia.

        Eficiencia: O(1), solo crea la referencia a la lista.
        """
        self.lista_productos = []

    def agregar_producto(self, producto):
        """Agrega un objeto Producto a la lista del inventario.

        Eficiencia: append en lista Python es O(1) amortizado.
        """
        self.lista_productos.append(producto)

    def buscar_por_codigo(self, codigo):
        """Busca un producto por su codigo unico.

        Retorna el objeto Producto si lo encuentra, None en caso contrario.

        Eficiencia: recorrido lineal O(n) con salida temprana
        mediante bandera booleana al encontrar coincidencia.
        """
        producto_encontrado = None
        encontrado = False
        i = 0
        while i < len(self.lista_productos) and not encontrado:
            if self.lista_productos[i].codigo == codigo:
                producto_encontrado = self.lista_productos[i]
                encontrado = True
            i = i + 1
        return producto_encontrado

    def buscar_por_coordenada(self, coordenada):
        """Busca un producto por su coordenada en la maquina.

        Retorna el objeto Producto si lo encuentra, None en caso contrario.

        Eficiencia: recorrido lineal O(n) con bandera de salida temprana.
        """
        producto_encontrado = None
        encontrado = False
        i = 0
        while i < len(self.lista_productos) and not encontrado:
            if self.lista_productos[i].coordenada == coordenada:
                producto_encontrado = self.lista_productos[i]
                encontrado = True
            i = i + 1
        return producto_encontrado

    def obtener_productos(self):
        """Retorna la lista completa de productos.

        Eficiencia: O(1), retorna referencia directa a la lista interna.
        """
        return self.lista_productos

    def obtener_cantidad_total(self):
        """Retorna la cantidad total de productos registrados.

        Eficiencia: len() en listas Python es O(1).
        """
        return len(self.lista_productos)

    def productos_disponibles(self):
        """Retorna una lista con los productos que tienen stock mayor a cero.

        Eficiencia: recorrido completo O(n), genera lista filtrada.
        """
        disponibles = []
        i = 0
        while i < len(self.lista_productos):
            if self.lista_productos[i].cantidad > 0:
                disponibles.append(self.lista_productos[i])
            i = i + 1
        return disponibles

    def productos_agotados(self):
        """Retorna una lista con los productos sin stock.

        Eficiencia: recorrido completo O(n), genera lista filtrada.
        """
        agotados = []
        i = 0
        while i < len(self.lista_productos):
            if self.lista_productos[i].cantidad == 0:
                agotados.append(self.lista_productos[i])
            i = i + 1
        return agotados
