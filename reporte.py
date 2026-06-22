# Integrantes: Ivanna Correnti y Rodrigo Da Camara
import matplotlib.pyplot as plt
from datetime import datetime

ARCHIVO_REPORTE = "reporte_ventas.txt"


def calcular_estadisticas(ventas, inventario):
    """Recorre el historial de ventas y calcula las estadisticas
    necesarias para el reporte y las graficas.

    Retorna un diccionario con:
        - ventas_por_producto: dict {nombre: cantidad_vendida}
        - ingresos_por_producto: dict {nombre: monto_total}
        - gasto_por_usuario: dict {hash_tarjeta: monto_total}
        - total_dinero: float con el ingreso total
        - stock_actual: dict {nombre: cantidad_restante}
        - ventas_cronologicas: lista de tuplas (fecha, monto) ordenada

    Eficiencia: recorrido unico O(v) donde v es el numero de ventas,
    acumulando en diccionarios con acceso O(1) por llave. El recorrido
    del inventario es O(n) adicional.
    """
    ventas_por_producto = {}
    ingresos_por_producto = {}
    gasto_por_usuario = {}
    total_dinero = 0.0
    ventas_cronologicas = []

    i = 0
    while i < len(ventas):
        venta = ventas[i]
        nombre = venta.producto.nombre

        if nombre in ventas_por_producto:
            ventas_por_producto[nombre] = ventas_por_producto[nombre] + 1
        else:
            ventas_por_producto[nombre] = 1

        if nombre in ingresos_por_producto:
            ingresos_por_producto[nombre] = ingresos_por_producto[nombre] + venta.monto
        else:
            ingresos_por_producto[nombre] = venta.monto

        clave_usuario = str(venta.hash_tarjeta)
        if clave_usuario in gasto_por_usuario:
            gasto_por_usuario[clave_usuario] = gasto_por_usuario[clave_usuario] + venta.monto
        else:
            gasto_por_usuario[clave_usuario] = venta.monto

        total_dinero = total_dinero + venta.monto
        ventas_cronologicas.append((venta.fecha, venta.monto))

        i = i + 1

    stock_actual = {}
    productos = inventario.obtener_productos()
    j = 0
    while j < len(productos):
        stock_actual[productos[j].nombre] = productos[j].cantidad
        j = j + 1

    estadisticas = {
        "ventas_por_producto": ventas_por_producto,
        "ingresos_por_producto": ingresos_por_producto,
        "gasto_por_usuario": gasto_por_usuario,
        "total_dinero": total_dinero,
        "stock_actual": stock_actual,
        "ventas_cronologicas": ventas_cronologicas
    }

    return estadisticas


def generar_reporte_texto(estadisticas):
    """Genera el archivo de texto con el resumen del reporte de cierre.

    Incluye: ventas por producto, ingresos por producto,
    gasto por usuario y total general.

    Eficiencia: escritura secuencial O(p + u) donde p es la cantidad
    de productos vendidos y u la cantidad de usuarios.
    """
    fecha_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    lineas = []
    lineas.append("=" * 60)
    lineas.append("       REPORTE DE CIERRE - MAQUINA EXPENDEDORA")
    lineas.append(f"       Fecha: {fecha_reporte}")
    lineas.append("=" * 60)

    lineas.append("\n--- VENTAS POR PRODUCTO ---")
    ventas_prod = estadisticas["ventas_por_producto"]
    stock = estadisticas["stock_actual"]
    for nombre in ventas_prod:
        unidades = ventas_prod[nombre]
        stock_rest = stock.get(nombre, 0)
        lineas.append(f"  {nombre[:30]:<32} Vendidos: {unidades:>3}  |  Stock restante: {stock_rest:>3}")

    lineas.append("\n--- INGRESOS POR PRODUCTO ---")
    ingresos = estadisticas["ingresos_por_producto"]
    for nombre in ingresos:
        monto = ingresos[nombre]
        lineas.append(f"  {nombre[:30]:<32} ${monto:>8.2f}")

    lineas.append("\n--- GASTO POR USUARIO ---")
    gastos = estadisticas["gasto_por_usuario"]
    for usuario in gastos:
        monto = gastos[usuario]
        lineas.append(f"  Tarjeta: {usuario:<25} ${monto:>8.2f}")

    lineas.append("\n" + "-" * 60)
    lineas.append(f"  TOTAL RECAUDADO: ${estadisticas['total_dinero']:>10.2f}")
    lineas.append("=" * 60)

    try:
        archivo = open(ARCHIVO_REPORTE, "w", encoding="utf-8")
        i = 0
        while i < len(lineas):
            archivo.write(lineas[i] + "\n")
            i = i + 1
        archivo.close()
        print(f"\n  Reporte de texto guardado en '{ARCHIVO_REPORTE}'.")
    except Exception:
        print("\n  Error al guardar el reporte de texto.")

    i = 0
    while i < len(lineas):
        print(lineas[i])
        i = i + 1


def grafica_barras_ventas(estadisticas):
    """Genera un grafico de barras con las unidades vendidas
    por producto y lo exporta como imagen PNG.

    Eficiencia: matplotlib opera sobre listas de tamanio p
    (productos vendidos), la renderizacion es O(p).
    """
    ventas_prod = estadisticas["ventas_por_producto"]

    if len(ventas_prod) == 0:
        print("  No hay datos de ventas para graficar.")
        return

    nombres = []
    cantidades = []
    for nombre in ventas_prod:
        nombres.append(nombre[:15])
        cantidades.append(ventas_prod[nombre])

    plt.figure(figsize=(12, 6))
    barras = plt.bar(nombres, cantidades, color='#3498db', edgecolor='#2c3e50', linewidth=0.8)

    i = 0
    while i < len(barras):
        altura = barras[i].get_height()
        plt.text(barras[i].get_x() + barras[i].get_width() / 2.0, altura + 0.1,
                 str(int(altura)), ha='center', va='bottom', fontweight='bold', fontsize=9)
        i = i + 1

    plt.title("Unidades Vendidas por Producto", fontsize=14, fontweight='bold')
    plt.xlabel("Producto", fontsize=11)
    plt.ylabel("Unidades Vendidas", fontsize=11)
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.tight_layout()
    plt.savefig("grafica_barras_ventas.png", dpi=150)
    plt.close()
    print("  Grafica de barras guardada en 'grafica_barras_ventas.png'.")


def grafica_circular_ingresos(estadisticas):
    """Genera un grafico circular (pie chart) con la distribucion
    porcentual de ingresos por producto y lo exporta como PNG.

    Eficiencia: matplotlib opera sobre listas de tamanio p,
    renderizacion O(p).
    """
    ingresos = estadisticas["ingresos_por_producto"]

    if len(ingresos) == 0:
        print("  No hay datos de ingresos para graficar.")
        return

    nombres = []
    montos = []
    for nombre in ingresos:
        nombres.append(nombre[:15])
        montos.append(ingresos[nombre])

    colores = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6',
               '#1abc9c', '#e67e22', '#34495e', '#16a085', '#c0392b',
               '#2980b9', '#27ae60', '#d35400', '#8e44ad', '#f1c40f']

    while len(colores) < len(nombres):
        colores = colores + colores

    plt.figure(figsize=(10, 8))
    plt.pie(montos, labels=nombres, colors=colores[:len(nombres)],
            autopct='%1.1f%%', startangle=140, textprops={'fontsize': 8})
    plt.title("Distribucion de Ingresos por Producto", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig("grafica_circular_ingresos.png", dpi=150)
    plt.close()
    print("  Grafica circular guardada en 'grafica_circular_ingresos.png'.")


def grafica_linea_ventas(estadisticas):
    """Genera un grafico de linea con la evolucion acumulada
    de ingresos a lo largo del tiempo y lo exporta como PNG.

    Eficiencia: recorrido O(v) para calcular acumulados,
    renderizacion O(v).
    """
    cronologicas = estadisticas["ventas_cronologicas"]

    if len(cronologicas) == 0:
        print("  No hay datos cronologicos para graficar.")
        return

    fechas = []
    acumulado = []
    suma = 0.0
    i = 0
    while i < len(cronologicas):
        fecha, monto = cronologicas[i]
        suma = suma + monto
        fechas.append(i + 1)
        acumulado.append(suma)
        i = i + 1

    plt.figure(figsize=(12, 6))
    plt.plot(fechas, acumulado, color='#2ecc71', linewidth=2, marker='o',
             markersize=5, markerfacecolor='#27ae60')
    plt.fill_between(fechas, acumulado, alpha=0.15, color='#2ecc71')
    plt.title("Ingresos Acumulados por Venta", fontsize=14, fontweight='bold')
    plt.xlabel("Numero de Venta", fontsize=11)
    plt.ylabel("Ingreso Acumulado ($)", fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("grafica_linea_ingresos.png", dpi=150)
    plt.close()
    print("  Grafica de linea guardada en 'grafica_linea_ingresos.png'.")


def generar_todas_las_graficas(estadisticas):
    """Genera las tres graficas (barras, circular, linea) en secuencia.

    Eficiencia: cada grafica se genera y cierra independientemente
    para liberar memoria de matplotlib entre renderizaciones.
    """
    print("\n  Generando graficas...")
    grafica_barras_ventas(estadisticas)
    grafica_circular_ingresos(estadisticas)
    grafica_linea_ventas(estadisticas)
    print("  Todas las graficas generadas exitosamente.")
