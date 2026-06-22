# Integrantes: Ivanna Correnti y Rodrigo Da Camara
import urllib.request
import json
from inventario import Inventario
from producto import Producto
from tarjeta import Tarjeta

URL_PRODUCTOS = "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-3/refs/heads/main/productos.json"
CANTIDAD_INICIAL = 5
PRODUCTOS_POR_FILA = 5


class Maquina:
    """Controlador principal de la maquina expendedora.

    Coordina la carga de productos desde la API de GitHub,
    la asignacion de coordenadas y la interaccion con el usuario
    a traves del menu principal.

    Eficiencia: centraliza la logica de control para evitar
    duplicacion de responsabilidades entre las entidades.
    """

    def __init__(self):
        """Inicializa la maquina con un inventario vacio y listas
        de transacciones vacias.

        Eficiencia: O(1), solo crea referencias a estructuras vacias.
        """
        self.inventario = Inventario()
        self.tarjetas = []
        self.ventas = []
        self.restocks = []

    def _asignar_coordenadas(self, indice):
        """Genera la coordenada tipo grilla (A1, A2, ..., B1, B2, ...).

        El indice numerico se convierte a letra de fila + numero
        de columna segun la cantidad de productos por fila.

        Eficiencia: O(1), calculo aritmetico directo con divmod.
        """
        fila = indice // PRODUCTOS_POR_FILA
        columna = (indice % PRODUCTOS_POR_FILA) + 1
        letra_fila = chr(ord('A') + fila)
        return f"{letra_fila}{columna}"

    def iniciar(self):
        """Conecta con la API de GitHub para cargar o actualizar productos.

        Si la conexion falla, captura la excepcion y asume que los
        precios no han cambiado, manteniendo el inventario previo.

        Eficiencia: una sola peticion HTTP para obtener todo el catalogo.
        El parseo del JSON es O(n) donde n es la cantidad de productos.
        """
        datos_cargados = False
        try:
            respuesta = urllib.request.urlopen(URL_PRODUCTOS)
            contenido = respuesta.read().decode('utf-8')
            lista_json = json.loads(contenido)
            datos_cargados = True
        except Exception:
            print("No se pudo conectar con la API. Se asumen precios sin cambios.")

        if datos_cargados:
            indice = 0
            while indice < len(lista_json):
                item = lista_json[indice]
                coordenada = self._asignar_coordenadas(indice)
                codigo = item["cod"]
                nombre = item["prod"]
                precio = item["precio"]
                despedida = item["despedida"]

                producto_existente = self.inventario.buscar_por_codigo(codigo)
                if producto_existente is not None:
                    producto_existente.precio = precio
                    producto_existente.nombre = nombre
                    producto_existente.despedida = despedida
                else:
                    nuevo = Producto(coordenada, codigo, nombre, precio, CANTIDAD_INICIAL, despedida)
                    self.inventario.agregar_producto(nuevo)

                indice = indice + 1

    def _dibujar_catalogo(self):
        """Dibuja el catalogo de productos en formato de grilla visual.

        Muestra coordenada, nombre truncado, precio y stock
        organizados en filas de PRODUCTOS_POR_FILA columnas.

        Eficiencia: recorrido O(n) sobre la lista de productos,
        con formateo de cadenas constante por producto.
        """
        productos = self.inventario.obtener_productos()
        print("\n" + "=" * 70)
        print("          MAQUINA EXPENDEDORA - CATALOGO DE PRODUCTOS")
        print("=" * 70)

        i = 0
        while i < len(productos):
            p = productos[i]
            if p.cantidad > 0:
                nombre_corto = p.nombre[:20]
                linea = f"  [{p.coordenada}] {nombre_corto:<22} ${p.precio:.2f}  ({p.cantidad}u)"
            else:
                linea = f"  [{p.coordenada}] {'--- AGOTADO ---':<22} ${p.precio:.2f}  (0u)"
            print(linea)

            if (i + 1) % PRODUCTOS_POR_FILA == 0:
                print("-" * 70)

            i = i + 1

        print("=" * 70)
        print("  Ingrese coordenada para comprar | RS: Restock | RP: Reporte")
        print("  Presione ENTER para salir")
        print("=" * 70)

    def mostrar_menu_principal(self):
        """Muestra el menu principal y procesa la seleccion del usuario.

        Valida los inputs: coordenada valida, 'RS' para restock,
        'RP' para reportes, o ENTER para salir. El bucle se controla
        con bandera booleana, sin uso de break.

        Eficiencia: el bucle principal es O(1) por iteracion para
        la validacion de entrada; las operaciones derivadas dependen
        de sus propias complejidades.
        """
        continuar = True
        while continuar:
            self._dibujar_catalogo()
            opcion = input("\n  >> Seleccion: ").strip()

            if opcion == "":
                print("\n  Gracias por usar la maquina expendedora. Hasta pronto!")
                continuar = False

            elif opcion.upper() == "RS":
                print("\n  [Funcion de Restock - Pendiente de implementar]")

            elif opcion.upper() == "RP":
                print("\n  [Funcion de Reportes - Pendiente de implementar]")

            else:
                producto = self.inventario.buscar_por_coordenada(opcion.upper())
                if producto is not None:
                    if producto.cantidad > 0:
                        print(f"\n  Seleccionaste: {producto.nombre} - ${producto.precio:.2f}")
                        print("  [Proceso de compra - Pendiente de implementar]")
                    else:
                        print(f"\n  El producto {producto.nombre} esta agotado.")
                else:
                    print("\n  Coordenada no valida. Intente de nuevo.")
