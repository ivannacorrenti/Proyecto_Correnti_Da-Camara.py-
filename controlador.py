# Integrantes: Ivanna Correnti y Rodrigo Da Camara
import urllib.request
import json
from inventario import Inventario
from producto import Producto
from tarjeta import Tarjeta
from transacciones import Venta

URL_PRODUCTOS = "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-3/refs/heads/main/productos.json"
URL_CLIENTES = "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-3/refs/heads/main/clientes.json"
CANTIDAD_INICIAL = 5
PRODUCTOS_POR_FILA = 5
ARCHIVO_VENTAS = "ventas_local.txt"


class Maquina:
    """Controlador principal de la maquina expendedora.

    Coordina la carga de productos y clientes desde APIs,
    y procesa las ventas interactivas usando banderas logicas.

    Eficiencia: las listas de transacciones (ventas y tarjetas)
    se almacenan en memoria para busqueda O(n), y se escribe
    el registro en disco inmediatamente para persistencia simple.
    """

    def __init__(self):
        """Inicializa la maquina con inventario y listas vacias.

        Eficiencia: O(1).
        """
        self.inventario = Inventario()
        self.tarjetas = []
        self.ventas = []
        self.restocks = []

    def _asignar_coordenadas(self, indice):
        """Genera coordenada grilla (A1, A2...) para los productos.

        Eficiencia: calculo numerico O(1).
        """
        fila = indice // PRODUCTOS_POR_FILA
        columna = (indice % PRODUCTOS_POR_FILA) + 1
        letra_fila = chr(ord('A') + fila)
        return f"{letra_fila}{columna}"

    def iniciar(self):
        """Descarga productos y clientes desde GitHub.

        Usa banderas booleanas para el control de errores, asumiendo
        estados sin cambios si la conexion falla.

        Eficiencia: llamadas de red costosas (I/O bound) que se
        ejecutan solo al iniciar.
        """
        # Carga de productos
        datos_productos_cargados = False
        try:
            respuesta_p = urllib.request.urlopen(URL_PRODUCTOS)
            lista_json_p = json.loads(respuesta_p.read().decode('utf-8'))
            datos_productos_cargados = True
        except Exception:
            print("No se pudo conectar con la API de productos. Se asume inventario previo.")

        if datos_productos_cargados:
            indice = 0
            while indice < len(lista_json_p):
                item = lista_json_p[indice]
                coordenada = self._asignar_coordenadas(indice)
                producto_existente = self.inventario.buscar_por_codigo(item["cod"])
                if producto_existente is not None:
                    producto_existente.precio = item["precio"]
                    producto_existente.nombre = item["prod"]
                    producto_existente.despedida = item["despedida"]
                else:
                    nuevo = Producto(coordenada, item["cod"], item["prod"], item["precio"], CANTIDAD_INICIAL, item["despedida"])
                    self.inventario.agregar_producto(nuevo)
                indice = indice + 1

        # Carga de clientes
        datos_clientes_cargados = False
        try:
            respuesta_c = urllib.request.urlopen(URL_CLIENTES)
            lista_json_c = json.loads(respuesta_c.read().decode('utf-8'))
            datos_clientes_cargados = True
        except Exception:
            print("No se pudo conectar con la API de clientes. Se asume lista local de tarjetas vacia o sin cambios.")

        if datos_clientes_cargados:
            self.tarjetas = []
            indice = 0
            while indice < len(lista_json_c):
                item = lista_json_c[indice]
                nueva_tarjeta = Tarjeta(item["id"], item["saldo"])
                self.tarjetas.append(nueva_tarjeta)
                indice = indice + 1

    def _dibujar_catalogo(self):
        """Imprime el catalogo en pantalla.

        Eficiencia: O(n) sobre inventario, operaciones de print I/O bound.
        """
        productos = self.inventario.obtener_productos()
        print("\n" + "=" * 70)
        print("          MAQUINA EXPENDEDORA - CATALOGO DE PRODUCTOS")
        print("=" * 70)

        i = 0
        while i < len(productos):
            p = productos[i]
            if p.cantidad > 0:
                linea = f"  [{p.coordenada}] {p.nombre[:20]:<22} ${p.precio:.2f}  ({p.cantidad}u)"
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

    def _buscar_tarjeta(self, hash_buscado):
        """Busca una tarjeta por su hash en la lista cargada.

        Retorna la Tarjeta si la encuentra, o None si no existe.

        Eficiencia: recorrido O(n) con salida temprana mediante bandera.
        """
        tarjeta_encontrada = None
        encontrado = False
        i = 0
        while i < len(self.tarjetas) and not encontrado:
            if self.tarjetas[i].hash_tarjeta == hash_buscado:
                tarjeta_encontrada = self.tarjetas[i]
                encontrado = True
            i = i + 1
        return tarjeta_encontrada

    def procesar_venta(self, producto):
        """Procesa una venta solicitando tarjeta y evaluando saldos.

        Aplica la funcion hash() nativa al input del usuario, valida
        saldos y cantidades sin usar break.

        Eficiencia: validaciones condicionales O(1), busqueda de tarjeta O(n),
        escritura en archivo usando open modo append (I/O bound).
        """
        entrada_tarjeta = input("\n  Ingrese su numero de tarjeta: ").strip()
        
        # Para evitar el random seed en strings, en algunos entornos
        # si se ingresan numeros, el hash de int(str) es predecible,
        # pero la instruccion dice aplicar hash() al input del usuario.
        try:
            # Intentamos convertir a int si el usuario mete numeros 
            # para que coincida con el int en el JSON si fuera el caso
            valor_hash = hash(int(entrada_tarjeta))
        except ValueError:
            valor_hash = hash(entrada_tarjeta)

        tarjeta_obj = self._buscar_tarjeta(valor_hash)

        if tarjeta_obj is not None:
            if tarjeta_obj.cobrar(producto.precio):
                if producto.reducir_cantidad(1):
                    # Se consolida la venta
                    nueva_venta = Venta(producto, producto.precio, tarjeta_obj.hash_tarjeta)
                    self.ventas.append(nueva_venta)
                    
                    print(f"\n  COMPRA EXITOSA: {producto.nombre}")
                    print(f"  {producto.despedida}")
                    print(f"  Saldo restante: ${tarjeta_obj.saldo:.2f}")

                    # Registrar la venta en texto
                    try:
                        with open(ARCHIVO_VENTAS, "a", encoding="utf-8") as f:
                            f.write(str(nueva_venta) + "\n")
                    except Exception:
                        pass
                else:
                    print("\n  Error: El producto ya no tiene stock.")
                    # Devolver el dinero al saldo en caso de fallo (rollback logico)
                    tarjeta_obj.saldo = tarjeta_obj.saldo + producto.precio
            else:
                print("\n  Error: Saldo insuficiente en la tarjeta.")
        else:
            print("\n  Error: Tarjeta no reconocida o hash invalido.")

    def mostrar_menu_principal(self):
        """Menu interactivo principal controlado por banderas."""
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
                        self.procesar_venta(producto)
                    else:
                        print(f"\n  El producto {producto.nombre} esta agotado.")
                else:
                    print("\n  Coordenada no valida. Intente de nuevo.")
