# Integrantes: Ivanna Correnti y Rodrigo Da Camara
import urllib.request
import json
from inventario import Inventario
from producto import Producto
from tarjeta import Tarjeta
from transacciones import Venta, Restock
import reporte

URL_PRODUCTOS = "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-3/refs/heads/main/productos.json"
URL_CLIENTES = "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-3/refs/heads/main/clientes.json"
CANTIDAD_INICIAL = 5
PRODUCTOS_POR_FILA = 5
ARCHIVO_VENTAS = "ventas_local.txt"
ARCHIVO_RESTOCK = "restock_local.txt"


class Maquina:
    """Controlador principal de la maquina expendedora.

    Coordina carga desde APIs, ventas, restock y persistencia
    en archivos de texto locales.

    Eficiencia: operaciones de inventario O(n) sobre listas en memoria,
    persistencia inmediata en disco tras cada operacion para evitar
    perdida de datos.
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

        Eficiencia: calculo numerico O(1) con divmod.
        """
        fila = indice // PRODUCTOS_POR_FILA
        columna = (indice % PRODUCTOS_POR_FILA) + 1
        letra_fila = chr(ord('A') + fila)
        return f"{letra_fila}{columna}"

    def _siguiente_coordenada(self):
        """Calcula la siguiente coordenada disponible en la grilla.

        Se basa en la cantidad actual de productos para determinar
        la posicion siguiente.

        Eficiencia: O(1), usa el total de productos como indice.
        """
        total = self.inventario.obtener_cantidad_total()
        return self._asignar_coordenadas(total)

    def iniciar(self):
        """Descarga productos y clientes desde GitHub, luego aplica
        las modificaciones de restock persistidas en el archivo local.

        Eficiencia: llamadas de red I/O bound al inicio, seguidas
        de lectura local O(m) donde m es la cantidad de lineas de restock.
        """
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

        datos_clientes_cargados = False
        try:
            respuesta_c = urllib.request.urlopen(URL_CLIENTES)
            lista_json_c = json.loads(respuesta_c.read().decode('utf-8'))
            datos_clientes_cargados = True
        except Exception:
            print("No se pudo conectar con la API de clientes. Se asume lista previa.")

        if datos_clientes_cargados:
            self.tarjetas = []
            indice = 0
            while indice < len(lista_json_c):
                item = lista_json_c[indice]
                nueva_tarjeta = Tarjeta(item["id"], item["saldo"])
                self.tarjetas.append(nueva_tarjeta)
                indice = indice + 1

        self._cargar_restock_local()

    def _cargar_restock_local(self):
        """Lee el archivo de restock local y aplica las operaciones
        persistidas al inventario actual.

        Formato por linea:
            AGREGAR|coordenada|cantidad
            CAMBIAR|coordenada|codigo|nombre|precio|cantidad|despedida
            NUEVO|coordenada|codigo|nombre|precio|cantidad|despedida

        Eficiencia: lectura secuencial O(m) donde m es cantidad de
        lineas, cada operacion de busqueda interna es O(n).
        """
        try:
            archivo = open(ARCHIVO_RESTOCK, "r", encoding="utf-8")
            lineas = archivo.readlines()
            archivo.close()
        except FileNotFoundError:
            lineas = []

        i = 0
        while i < len(lineas):
            linea = lineas[i].strip()
            if linea != "":
                partes = linea.split("|")
                tipo = partes[0]

                if tipo == "AGREGAR" and len(partes) == 3:
                    coordenada = partes[1]
                    cantidad = int(partes[2])
                    producto = self.inventario.buscar_por_coordenada(coordenada)
                    if producto is not None:
                        producto.cantidad = producto.cantidad + cantidad

                elif tipo == "CAMBIAR" and len(partes) == 7:
                    coordenada = partes[1]
                    producto = self.inventario.buscar_por_coordenada(coordenada)
                    if producto is not None:
                        producto.codigo = partes[2]
                        producto.nombre = partes[3]
                        producto.precio = float(partes[4])
                        producto.cantidad = int(partes[5])
                        producto.despedida = partes[6]

                elif tipo == "NUEVO" and len(partes) == 7:
                    coordenada = partes[1]
                    existente = self.inventario.buscar_por_coordenada(coordenada)
                    if existente is None:
                        nuevo = Producto(coordenada, partes[2], partes[3], float(partes[4]), int(partes[5]), partes[6])
                        self.inventario.agregar_producto(nuevo)

            i = i + 1

    def _guardar_linea_restock(self, linea):
        """Agrega una linea de operacion al archivo de restock local.

        Eficiencia: apertura en modo append, O(1) por escritura.
        """
        try:
            archivo = open(ARCHIVO_RESTOCK, "a", encoding="utf-8")
            archivo.write(linea + "\n")
            archivo.close()
        except Exception:
            print("  Error al guardar en archivo de restock.")

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

        Eficiencia: validaciones O(1), busqueda de tarjeta O(n),
        escritura append en archivo I/O bound.
        """
        entrada_tarjeta = input("\n  Ingrese su numero de tarjeta: ").strip()

        try:
            valor_hash = hash(int(entrada_tarjeta))
        except ValueError:
            valor_hash = hash(entrada_tarjeta)

        tarjeta_obj = self._buscar_tarjeta(valor_hash)

        if tarjeta_obj is not None:
            if tarjeta_obj.cobrar(producto.precio):
                if producto.reducir_cantidad(1):
                    nueva_venta = Venta(producto, producto.precio, tarjeta_obj.hash_tarjeta)
                    self.ventas.append(nueva_venta)

                    print(f"\n  COMPRA EXITOSA: {producto.nombre}")
                    print(f"  {producto.despedida}")
                    print(f"  Saldo restante: ${tarjeta_obj.saldo:.2f}")

                    try:
                        archivo = open(ARCHIVO_VENTAS, "a", encoding="utf-8")
                        archivo.write(str(nueva_venta) + "\n")
                        archivo.close()
                    except Exception:
                        pass
                else:
                    print("\n  Error: El producto ya no tiene stock.")
                    tarjeta_obj.saldo = tarjeta_obj.saldo + producto.precio
            else:
                print("\n  Error: Saldo insuficiente en la tarjeta.")
        else:
            print("\n  Error: Tarjeta no reconocida o hash invalido.")

    def ejecutar_restock(self):
        """Menu de restock con tres opciones: agregar stock, cambiar
        producto en coordenada existente, o agregar producto nuevo
        expandiendo la grilla.

        Persiste cada operacion al archivo de texto local para que
        los cambios sobrevivan al reinicio del programa.

        Eficiencia: cada sub-operacion es O(n) por la busqueda en
        inventario, la escritura en archivo es O(1) por append.
        """
        continuar_restock = True
        while continuar_restock:
            print("\n" + "=" * 50)
            print("          MENU DE RESTOCK")
            print("=" * 50)
            print("  1. Agregar stock a producto existente")
            print("  2. Cambiar producto en una coordenada")
            print("  3. Agregar producto nuevo (expandir grilla)")
            print("  4. Volver al menu principal")
            print("=" * 50)

            opcion = input("\n  >> Opcion: ").strip()

            if opcion == "1":
                self._restock_agregar_cantidad()
            elif opcion == "2":
                self._restock_cambiar_producto()
            elif opcion == "3":
                self._restock_nuevo_producto()
            elif opcion == "4":
                continuar_restock = False
            else:
                print("\n  Opcion no valida.")

    def _restock_agregar_cantidad(self):
        """Agrega unidades al stock de un producto existente
        identificado por su coordenada.

        Eficiencia: busqueda O(n) + escritura O(1).
        """
        coordenada = input("  Coordenada del producto: ").strip().upper()
        producto = self.inventario.buscar_por_coordenada(coordenada)

        if producto is not None:
            entrada_cantidad = input(f"  Cantidad a agregar a '{producto.nombre}': ").strip()
            entrada_valida = False
            cantidad = 0

            if entrada_cantidad.isdigit():
                cantidad = int(entrada_cantidad)
                if cantidad > 0:
                    entrada_valida = True

            if entrada_valida:
                producto.cantidad = producto.cantidad + cantidad
                registro = Restock(producto, cantidad)
                self.restocks.append(registro)

                self._guardar_linea_restock(f"AGREGAR|{coordenada}|{cantidad}")

                print(f"\n  Restock exitoso: {producto.nombre} ahora tiene {producto.cantidad} unidades.")
            else:
                print("\n  Cantidad no valida. Debe ser un numero entero positivo.")
        else:
            print("\n  Coordenada no encontrada.")

    def _restock_cambiar_producto(self):
        """Reemplaza completamente el producto en una coordenada
        existente de la grilla.

        Eficiencia: busqueda O(n) + actualizacion de atributos O(1)
        + escritura O(1).
        """
        coordenada = input("  Coordenada a reemplazar: ").strip().upper()
        producto = self.inventario.buscar_por_coordenada(coordenada)

        if producto is not None:
            print(f"\n  Producto actual: {producto.nombre}")
            nuevo_codigo = input("  Nuevo codigo: ").strip()
            nuevo_nombre = input("  Nuevo nombre: ").strip()
            nuevo_precio_str = input("  Nuevo precio: ").strip()
            nueva_cantidad_str = input("  Cantidad inicial: ").strip()
            nueva_despedida = input("  Mensaje de despedida: ").strip()

            datos_validos = True

            precio_nuevo = 0.0
            cantidad_nueva = 0

            if nuevo_codigo == "" or nuevo_nombre == "" or nueva_despedida == "":
                datos_validos = False

            if datos_validos:
                try:
                    precio_nuevo = float(nuevo_precio_str)
                    if precio_nuevo <= 0:
                        datos_validos = False
                except ValueError:
                    datos_validos = False

            if datos_validos:
                if nueva_cantidad_str.isdigit():
                    cantidad_nueva = int(nueva_cantidad_str)
                    if cantidad_nueva <= 0:
                        datos_validos = False
                else:
                    datos_validos = False

            if datos_validos:
                producto.codigo = nuevo_codigo
                producto.nombre = nuevo_nombre
                producto.precio = precio_nuevo
                producto.cantidad = cantidad_nueva
                producto.despedida = nueva_despedida

                registro = Restock(producto, cantidad_nueva)
                self.restocks.append(registro)

                linea = f"CAMBIAR|{coordenada}|{nuevo_codigo}|{nuevo_nombre}|{precio_nuevo}|{cantidad_nueva}|{nueva_despedida}"
                self._guardar_linea_restock(linea)

                print(f"\n  Producto reemplazado exitosamente en [{coordenada}].")
            else:
                print("\n  Datos no validos. Operacion cancelada.")
        else:
            print("\n  Coordenada no encontrada.")

    def _restock_nuevo_producto(self):
        """Agrega un producto completamente nuevo a la maquina,
        expandiendo la grilla con la siguiente coordenada disponible.

        Eficiencia: calculo de coordenada O(1), append O(1) amortizado,
        escritura en archivo O(1).
        """
        nueva_coordenada = self._siguiente_coordenada()
        print(f"\n  Se asignara la coordenada: [{nueva_coordenada}]")

        nuevo_codigo = input("  Codigo del producto: ").strip()
        nuevo_nombre = input("  Nombre del producto: ").strip()
        nuevo_precio_str = input("  Precio: ").strip()
        nueva_cantidad_str = input("  Cantidad inicial: ").strip()
        nueva_despedida = input("  Mensaje de despedida: ").strip()

        datos_validos = True
        precio_nuevo = 0.0
        cantidad_nueva = 0

        if nuevo_codigo == "" or nuevo_nombre == "" or nueva_despedida == "":
            datos_validos = False

        if datos_validos:
            codigo_existente = self.inventario.buscar_por_codigo(nuevo_codigo)
            if codigo_existente is not None:
                print("\n  Ya existe un producto con ese codigo.")
                datos_validos = False

        if datos_validos:
            try:
                precio_nuevo = float(nuevo_precio_str)
                if precio_nuevo <= 0:
                    datos_validos = False
            except ValueError:
                datos_validos = False

        if datos_validos:
            if nueva_cantidad_str.isdigit():
                cantidad_nueva = int(nueva_cantidad_str)
                if cantidad_nueva <= 0:
                    datos_validos = False
            else:
                datos_validos = False

        if datos_validos:
            nuevo_producto = Producto(nueva_coordenada, nuevo_codigo, nuevo_nombre, precio_nuevo, cantidad_nueva, nueva_despedida)
            self.inventario.agregar_producto(nuevo_producto)

            registro = Restock(nuevo_producto, cantidad_nueva)
            self.restocks.append(registro)

            linea = f"NUEVO|{nueva_coordenada}|{nuevo_codigo}|{nuevo_nombre}|{precio_nuevo}|{cantidad_nueva}|{nueva_despedida}"
            self._guardar_linea_restock(linea)

            print(f"\n  Producto '{nuevo_nombre}' agregado en [{nueva_coordenada}].")
        else:
            if datos_validos is False:
                print("\n  Datos no validos. Operacion cancelada.")

    def generar_reporte(self):
        """Recopila la informacion actual y delega la generacion del
        reporte de texto y las graficas al modulo especializado.

        Eficiencia: delegacion a funciones externas, la complejidad
        depende del modulo de reporte O(v + n).
        """
        print("\n  Generando reporte de cierre...")
        estadisticas = reporte.calcular_estadisticas(self.ventas, self.inventario)
        reporte.generar_reporte_texto(estadisticas)
        reporte.generar_todas_las_graficas(estadisticas)

    def mostrar_menu_principal(self):
        """Menu interactivo principal controlado por banderas.

        Eficiencia: bucle O(1) por iteracion, las operaciones
        derivadas dependen de sus propias complejidades.
        """
        continuar = True
        while continuar:
            self._dibujar_catalogo()
            opcion = input("\n  >> Seleccion: ").strip()

            if opcion == "":
                print("\n  Gracias por usar la maquina expendedora. Hasta pronto!")
                continuar = False
            elif opcion.upper() == "RS":
                self.ejecutar_restock()
            elif opcion.upper() == "RP":
                self.generar_reporte()
            else:
                producto = self.inventario.buscar_por_coordenada(opcion.upper())
                if producto is not None:
                    if producto.cantidad > 0:
                        self.procesar_venta(producto)
                    else:
                        print(f"\n  El producto {producto.nombre} esta agotado.")
                else:
                    print("\n  Coordenada no valida. Intente de nuevo.")
