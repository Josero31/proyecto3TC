"""
Simulador de Maquinas de Turing de una cinta.

Uso:
    python main.py                                    (simula todas las MT de maquinas/)
    python main.py maquinas/reconocedora_ww.yaml      (simula solo esa MT)
    python main.py --salida resultado.txt             (guarda tambien la salida)
"""

import argparse
import sys
from pathlib import Path

from maquina import ErrorConfiguracion
from parser_yaml import cargar
from simulador import simular

CARPETA_MAQUINAS = Path(__file__).resolve().parent / "maquinas"


def formatear(resultado, numero):
    lineas = [f"Cadena {numero}: \"{resultado.entrada}\"",
              "Descripciones instantaneas:"]
    for i, id_ in enumerate(resultado.ids):
        prefijo = "   " if i == 0 else "⊢  "
        lineas.append(f"  {i:>4}  {prefijo}{id_}")
    lineas += [
        f"Resultado: {'ACEPTADA' if resultado.aceptada else 'RECHAZADA'}",
        f"Motivo: {resultado.motivo}",
        f"Cinta final: {resultado.cinta_final}",
        f"Pasos: {resultado.pasos}",
    ]
    return "\n".join(lineas)


def ejecutar_archivo(ruta, max_pasos):
    """Simula todas las cadenas de un archivo YAML y devuelve el texto de salida."""
    maquina, entradas = cargar(ruta)
    bloques = [f"MT: {Path(ruta).name}",
               "Descripcion formal de la MT", maquina.descripcion()]
    for numero, entrada in enumerate(entradas, start=1):
        resultado = simular(maquina, entrada, max_pasos)
        bloques.append(formatear(resultado, numero))
    return "\n\n".join(bloques)


def main():
    parser = argparse.ArgumentParser(
        description="Simulador de Maquinas de Turing de una cinta")
    parser.add_argument("archivos", nargs="*",
                        help="archivos YAML con la descripcion de la MT "
                             "(si no se indica ninguno se usan todos los de maquinas/)")
    parser.add_argument("--max-pasos", type=int, default=100000,
                        help="limite de pasos por cadena (por defecto 100000)")
    parser.add_argument("--salida", help="guarda tambien el resultado en este archivo")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    archivos = args.archivos or sorted(str(p) for p in CARPETA_MAQUINAS.glob("*.yaml"))
    if not archivos:
        print(f"No se encontraron archivos YAML en {CARPETA_MAQUINAS}")
        sys.exit(1)

    textos = []
    for ruta in archivos:
        try:
            textos.append(ejecutar_archivo(ruta, args.max_pasos))
        except (ErrorConfiguracion, OSError) as error:
            textos.append(f"MT: {ruta}\n\nError en la configuracion: {error}")

    separador = "\n\n" + "-" * 70 + "\n\n"
    texto = separador.join(textos)
    print(texto)
    if args.salida:
        with open(args.salida, "w", encoding="utf-8") as archivo:
            archivo.write(texto + "\n")


if __name__ == "__main__":
    main()
