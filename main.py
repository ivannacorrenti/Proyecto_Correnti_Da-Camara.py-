# Integrantes: Ivanna Correnti y Rodrigo Da Camara
from controlador import Maquina


def main():
    """Punto de entrada principal del programa.

    Inicializa la maquina expendedora, carga los datos desde
    las APIs e inicia el bucle del menu principal interactivo.
    """
    maquina = Maquina()
    maquina.iniciar()
    maquina.mostrar_menu_principal()


if __name__ == "__main__":
    main()
