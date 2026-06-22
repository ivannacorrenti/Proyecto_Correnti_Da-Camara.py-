# Integrantes: Ivanna Correnti y Rodrigo Da Camara
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

ARCHIVO_REPORTE = "reporte_ventas.txt"


def calcular_estadisticas(ventas, inventario, restocks, tarjetas, cantidad_inicial):
    """Calcula las estadisticas necesarias para el reporte.

    Eficiencia: O(v + n) recorridos lineales sin anidamiento.
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
    cargado_por_producto = {}
    productos = inventario.obtener_productos()
    j = 0
    while j < len(productos):
        nombre = productos[j].nombre
        stock_actual[nombre] = productos[j].cantidad
        
        # El total cargado historicamente es la suma del stock actual
        # y todo lo que ha salido (las ventas).
        vendidos = ventas_por_producto.get(nombre, 0)
        cargado_por_producto[nombre] = productos[j].cantidad + vendidos
        
        j = j + 1

    estadisticas = {
        "ventas_por_producto": ventas_por_producto,
        "ingresos_por_producto": ingresos_por_producto,
        "gasto_por_usuario": gasto_por_usuario,
        "total_dinero": total_dinero,
        "stock_actual": stock_actual,
        "cargado_por_producto": cargado_por_producto,
        "ventas_cronologicas": ventas_cronologicas,
        "total_usuarios": len(tarjetas)
    }

    return estadisticas


def generar_reporte_texto(estadisticas):
    """Genera el reporte en txt."""
    fecha_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    lineas = []
    lineas.append("=" * 70)
    lineas.append("       REPORTE DE CIERRE - MAQUINA EXPENDEDORA")
    lineas.append(f"       Fecha: {fecha_reporte}")
    lineas.append("=" * 70)

    lineas.append("\n--- RESUMEN POR PRODUCTO (CARGADO VS VENDIDO) ---")
    cargado = estadisticas["cargado_por_producto"]
    ventas_prod = estadisticas["ventas_por_producto"]
    stock = estadisticas["stock_actual"]
    
    for nombre in cargado:
        unidades_cargadas = cargado[nombre]
        unidades_vendidas = ventas_prod.get(nombre, 0)
        stock_rest = stock.get(nombre, 0)
        lineas.append(f"  {nombre[:25]:<27} Cargados: {unidades_cargadas:>3} | Vendidos: {unidades_vendidas:>3} | Restan: {stock_rest:>3}")

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

    lineas.append("\n" + "-" * 70)
    
    total_vendidos = sum(ventas_prod.values())
    lineas.append(f"  TOTAL PRODUCTOS VENDIDOS: {total_vendidos:>5}")
    lineas.append(f"  TOTAL USUARIOS REGISTRADOS: {estadisticas['total_usuarios']:>3}")
    lineas.append(f"  TOTAL DINERO RECAUDADO:   ${estadisticas['total_dinero']:>10.2f}")
    lineas.append("=" * 70)

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
    """Grafico de barras agrupadas: Cargado vs Vendido."""
    cargado = estadisticas["cargado_por_producto"]
    ventas = estadisticas["ventas_por_producto"]

    if len(cargado) == 0:
        return

    nombres = []
    vals_cargados = []
    vals_vendidos = []

    for nombre in cargado:
        nombres.append(nombre[:10])
        vals_cargados.append(cargado[nombre])
        vals_vendidos.append(ventas.get(nombre, 0))

    x = np.arange(len(nombres))
    width = 0.35

    fig, ax = plt.subplots(figsize=(14, 6))
    rects1 = ax.bar(x - width/2, vals_cargados, width, label='Cargados', color='#3498db')
    rects2 = ax.bar(x + width/2, vals_vendidos, width, label='Vendidos', color='#e74c3c')

    ax.set_ylabel('Unidades')
    ax.set_title('Unidades Cargadas vs Vendidas por Producto', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(nombres, rotation=45, ha='right', fontsize=8)
    ax.legend()

    plt.tight_layout()
    plt.savefig("grafica_barras_ventas.png", dpi=150)
    plt.close()
    print("  Grafica de barras guardada en 'grafica_barras_ventas.png'.")


def grafica_circular_gastos_usuario(estadisticas):
    gastos = estadisticas["gasto_por_usuario"]

    if len(gastos) == 0:
        return

    nombres = []
    montos = []
    for usuario in gastos:
        nombres.append(usuario[:15])
        montos.append(gastos[usuario])

    colores = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6',
               '#1abc9c', '#e67e22', '#34495e', '#16a085', '#c0392b',
               '#2980b9', '#27ae60', '#d35400', '#8e44ad', '#f1c40f']

    while len(colores) < len(nombres):
        colores = colores + colores

    plt.figure(figsize=(10, 8))
    plt.pie(montos, labels=nombres, colors=colores[:len(nombres)],
            autopct='%1.1f%%', startangle=140, textprops={'fontsize': 8})
    plt.title("Gasto por Usuario (Tarjeta)", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig("grafica_circular_gastos_usuario.png", dpi=150)
    plt.close()
    print("  Grafica circular guardada en 'grafica_circular_gastos_usuario.png'.")


def grafica_linea_ventas(estadisticas):
    cronologicas = estadisticas["ventas_cronologicas"]

    if len(cronologicas) == 0:
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
    print("\n  Generando graficas...")
    grafica_barras_ventas(estadisticas)
    grafica_circular_gastos_usuario(estadisticas)
    grafica_linea_ventas(estadisticas)
    print("  Todas las graficas generadas exitosamente.")
