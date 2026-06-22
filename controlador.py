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
PRODUCTOS_POR_FILA = 4
ARCHIVO_VENTAS = "ventas_local.txt"
ARCHIVO_INVENTARIO = "inventario_local.txt"


class Maquina:
    """Controlador principal de la maquina expendedora.

    Coordina carga desde APIs, ventas, restock y persistencia
    en archivos locales.
    """

    def __init__(self):
        self.inventario = Inventario()
        self.tarjetas = []
        self.ventas = []

    def _asignar_coordenadas(self, indice):
        """Asigna coordenada: letras como columnas, numeros como filas."""
        fila_num = (indice // PRODUCTOS_POR_FILA) + 1
        col_letra = chr(ord('A') + (indice % PRODUCTOS_POR_FILA))
        return f"{col_letra}{fila_num}"

    def iniciar(self):
        print("Iniciando sistema...")
        print("Cargando inventario local...")
        self._cargar_inventario_local()

        print("Revisando la red para actualizacion de precios y clientes...")
        datos_productos_cargados = False
        try:
            respuesta_p = urllib.request.urlopen(URL_PRODUCTOS)
            lista_json_p = json.loads(respuesta_p.read().decode('utf-8'))
            datos_productos_cargados = True
        except Exception:
            print("No se pudo conectar con la API de productos. Se asumen precios locales.")

        if datos_productos_cargados:
            indice = 0
            while indice < len(lista_json_p):
                item = lista_json_p[indice]
                producto_existente = self.inventario.buscar_por_codigo(item["cod"])
                if producto_existente is not None:
                    producto_existente.precio = item["precio"]
                else:
                    coordenada = self._asignar_coordenadas(self.inventario.obtener_cantidad_total())
                    nuevo = Producto(coordenada, item["cod"], item["prod"], item["precio"], CANTIDAD_INICIAL, item["despedida"])
                    self.inventario.agregar_producto(nuevo)
                indice = indice + 1
            print("Precios de productos actualizados exitosamente.")
            self._guardar_inventario_local()

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
            print("Clientes cargados exitosamente.")

    def _cargar_inventario_local(self):
        try:
            archivo = open(ARCHIVO_INVENTARIO, "r", encoding="utf-8")
            lineas = archivo.readlines()
            archivo.close()
            
            i = 0
            while i < len(lineas):
                linea = lineas[i].strip()
                if linea != "":
                    partes = linea.split("|")
                    if len(partes) == 6:
                        prod = Producto(partes[0], partes[1], partes[2], float(partes[3]), int(partes[4]), partes[5])
                        self.inventario.agregar_producto(prod)
                i = i + 1
        except FileNotFoundError:
            pass

    def _guardar_inventario_local(self):
        try:
            archivo = open(ARCHIVO_INVENTARIO, "w", encoding="utf-8")
            productos = self.inventario.obtener_productos()
            i = 0
            while i < len(productos):
                p = productos[i]
                archivo.write(f"{p.coordenada}|{p.codigo}|{p.nombre}|{p.precio}|{p.cantidad}|{p.despedida}\n")
                i = i + 1
            archivo.close()
        except Exception:
            pass

    def _dibujar_catalogo(self):
        """Dibuja el catalogo como matriz fija de 5 filas x 4 columnas
        con bordes decorativos de maquina expendedora.

        Eficiencia: busqueda por coordenada O(n) por cada celda,
        total O(20n) para la grilla fija de 20 posiciones.
        """
        ancho = 36
        print("\n" + "=" * ancho)
        print("|" + "MAQUINA EXPENDEDORA".center(ancho - 2) + "|")
        print("=" * ancho)

        header = "|    "
        c = 0
        while c < 4:
            header = header + f"{chr(ord('A') + c):<7}"
            c = c + 1
        header = header.rstrip()
        header = header + " " * (ancho - 1 - len(header)) + "|"
        print(header)

        f = 1
        while f <= 5:
            linea = f"| {f}  "
            c = 0
            while c < 4:
                letra_col = chr(ord('A') + c)
                coord_buscada = f"{letra_col}{f}"
                prod = self.inventario.buscar_por_coordenada(coord_buscada)
                if prod is not None:
                    if prod.cantidad > 0:
                        linea = linea + f"{prod.codigo[:5]:<7}"
                    else:
                        linea = linea + "       "
                else:
                    linea = linea + "       "
                c = c + 1
            linea = linea.rstrip()
            linea = linea + " " * (ancho - 1 - len(linea)) + "|"
            print(linea)
            f = f + 1

        print("=" * ancho)
        print("  Ingrese COORDENADA para comprar.")
        print("  Ingrese CODIGO para ver precio.")
        print("  RS: Restock | RP: Reporte | ENTER: Salir")
        print("=" * ancho)

    def _buscar_tarjeta(self, hash_buscado):
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
        print(f"\n  Producto seleccionado: {producto.nombre} | Precio: ${producto.precio:.2f}")
        entrada_tarjeta = input("  Ingrese su numero de tarjeta (ENTER para cancelar): ").strip()
        
        venta_activa = True
        if entrada_tarjeta == "":
            print("\n  Venta cancelada.")
            venta_activa = False
            
        if venta_activa:
            try:
                valor_hash = hash(int(entrada_tarjeta))
            except ValueError:
                valor_hash = hash(entrada_tarjeta)

            tarjeta_obj = self._buscar_tarjeta(valor_hash)

            if tarjeta_obj is not None:
                if tarjeta_obj.saldo >= producto.precio:
                    confirmacion = input(f"  Desea comprar {producto.nombre} por ${producto.precio:.2f}? (S/N): ").strip().upper()
                    if confirmacion == "S":
                        if tarjeta_obj.cobrar(producto.precio):
                            if producto.reducir_cantidad(1):
                                nueva_venta = Venta(producto, producto.precio, tarjeta_obj.hash_tarjeta)
                                self.ventas.append(nueva_venta)

                                print("\n  Dispensando producto...")
                                print(f"  {producto.despedida}")
                                print(f"  Saldo restante: ${tarjeta_obj.saldo:.2f}")

                                try:
                                    archivo = open(ARCHIVO_VENTAS, "a", encoding="utf-8")
                                    archivo.write(str(nueva_venta) + "\n")
                                    archivo.close()
                                except Exception:
                                    pass
                                self._guardar_inventario_local()
                            else:
                                tarjeta_obj.saldo = tarjeta_obj.saldo + producto.precio
                                print("\n  Error: El producto se agoto.")
                    else:
                        print("\n  Compra cancelada por el usuario.")
                else:
                    print("\n  Error: Saldo insuficiente en la tarjeta.")
            else:
                print("\n  Error: Tarjeta no reconocida o hash invalido.")

    def ejecutar_restock(self):
        print("\n" + "=" * 50)
        print("          MENU DE RESTOCK")
        print("=" * 50)
        coordenada = input("  Ingrese la coordenada a modificar (ej. A1, B2): ").strip().upper()
        
        if coordenada != "":
            producto = self.inventario.buscar_por_coordenada(coordenada)
            if producto is not None:
                print(f"  Producto actual en {coordenada}: {producto.nombre} ({producto.cantidad}u)")
                print("  1. Actualizar existencia")
                print("  2. Cambiar producto")
                opcion = input("  >> Seleccion: ").strip()
                if opcion == "1":
                    self._restock_agregar_cantidad(producto)
                elif opcion == "2":
                    self._restock_cambiar_producto(producto)
                else:
                    print("\n  Opcion invalida.")
            else:
                print(f"\n  Error: La coordenada {coordenada} no existe.")

    def _restock_agregar_cantidad(self, producto):
        entrada_cantidad = input(f"  Cantidad a agregar a '{producto.nombre}': ").strip()
        entrada_valida = False
        cantidad = 0

        if entrada_cantidad.isdigit():
            cantidad = int(entrada_cantidad)
            if cantidad > 0:
                entrada_valida = True

        if entrada_valida:
            producto.cantidad = producto.cantidad + cantidad
            self._guardar_inventario_local()
            print(f"\n  Restock exitoso: {producto.nombre} ahora tiene {producto.cantidad} unidades.")
        else:
            print("\n  Cantidad no valida. Debe ser entero positivo.")

    def _restock_cambiar_producto(self, producto):
        print(f"\n  Sustituyendo: {producto.nombre}")
        nuevo_codigo = input("  Nuevo codigo (5 letras): ").strip()
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

            self._guardar_inventario_local()
            print(f"\n  Producto reemplazado exitosamente en [{producto.coordenada}].")
        else:
            print("\n  Datos no validos. Operacion cancelada.")

    def generar_reporte(self):
        print("\n  Generando reporte de cierre...")
        estadisticas = reporte.calcular_estadisticas(
            self.ventas, 
            self.inventario, 
            [], 
            self.tarjetas, 
            CANTIDAD_INICIAL
        )
        reporte.generar_reporte_texto(estadisticas)
        reporte.generar_todas_las_graficas(estadisticas)

    def mostrar_menu_principal(self):
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
                # Buscamos primero si es coordenada
                prod_por_coord = self.inventario.buscar_por_coordenada(opcion.upper())
                if prod_por_coord is not None:
                    if prod_por_coord.cantidad > 0:
                        self.procesar_venta(prod_por_coord)
                    else:
                        print(f"\n  El producto en {prod_por_coord.coordenada} esta agotado.")
                else:
                    # Buscamos si es codigo para ver el precio
                    prod_por_codigo = None
                    productos = self.inventario.obtener_productos()
                    i = 0
                    encontrado_c = False
                    while i < len(productos) and not encontrado_c:
                        if productos[i].codigo.upper() == opcion.upper():
                            prod_por_codigo = productos[i]
                            encontrado_c = True
                        i = i + 1
                    
                    if prod_por_codigo is not None:
                        print(f"\n  >>> PRECIO DE {prod_por_codigo.nombre}: ${prod_por_codigo.precio:.2f}")
                    else:
                        print("\n  Opcion no reconocida.")
