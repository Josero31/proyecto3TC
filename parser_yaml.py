"""
Lectura del archivo YAML y construccion de la MT.

Formato de cada transicion (segun el enunciado):

    - state: q0
      read: [a, B]     -> [simbolo leido en la cinta, simbolo en memoria]
      write: [a, B]    -> [nuevo simbolo en memoria, simbolo escrito en la cinta]
      move: R
      next: q1

que corresponde a  delta([q0, B], a) = ([q1, a], B, R).
"""

import yaml

from maquina import (BLANCO_POR_DEFECTO, ErrorConfiguracion, MaquinaTuring,
                     Transicion)

CLAVES_OBLIGATORIAS = ("states", "input_alphabet", "tape_alphabet",
                       "initial_state", "accept_states", "transitions")


def _texto(valor):
    return "" if valor is None else str(valor)


def _lista(valor, nombre):
    if not isinstance(valor, list):
        raise ErrorConfiguracion(f"'{nombre}' debe ser una lista")
    return [_texto(v) for v in valor]


def _par(valor, nombre, blanco, indice):
    """Normaliza read/write a una lista de dos simbolos."""
    if isinstance(valor, list):
        if len(valor) != 2:
            raise ErrorConfiguracion(
                f"Transicion {indice}: '{nombre}' debe tener dos simbolos")
        return _texto(valor[0]), _texto(valor[1])
    # Si se da un solo simbolo, la memoria se toma como blanco.
    if nombre == "read":
        return _texto(valor), blanco
    return blanco, _texto(valor)


def _transicion(datos, indice, blanco):
    for clave in ("state", "read", "write", "move", "next"):
        if clave not in datos:
            raise ErrorConfiguracion(
                f"Transicion {indice}: falta la clave '{clave}'")
    lee_cinta, lee_memoria = _par(datos["read"], "read", blanco, indice)
    escribe_memoria, escribe_cinta = _par(datos["write"], "write",
                                          blanco, indice)
    return Transicion(
        estado=_texto(datos["state"]),
        lee_cinta=lee_cinta,
        lee_memoria=lee_memoria,
        escribe_memoria=escribe_memoria,
        escribe_cinta=escribe_cinta,
        movimiento=_texto(datos["move"]).upper(),
        siguiente=_texto(datos["next"]),
    )


def cargar(ruta):
    """Devuelve (MaquinaTuring, lista de cadenas de entrada)."""
    with open(ruta, encoding="utf-8") as archivo:
        documento = yaml.safe_load(archivo)

    if not isinstance(documento, dict) or "mt" not in documento:
        raise ErrorConfiguracion("El archivo debe tener una clave raiz 'mt'")
    mt = documento["mt"]

    for clave in CLAVES_OBLIGATORIAS:
        if clave not in mt:
            raise ErrorConfiguracion(f"Falta la clave '{clave}' en 'mt'")

    blanco = _texto(mt.get("blank", BLANCO_POR_DEFECTO))
    transiciones = [_transicion(t, i + 1, blanco)
                    for i, t in enumerate(mt["transitions"])]

    maquina = MaquinaTuring(
        estados=_lista(mt["states"], "states"),
        alfabeto_entrada=_lista(mt["input_alphabet"], "input_alphabet"),
        alfabeto_cinta=_lista(mt["tape_alphabet"], "tape_alphabet"),
        estado_inicial=_texto(mt["initial_state"]),
        estados_aceptacion=_lista(mt["accept_states"], "accept_states"),
        transiciones=transiciones,
        blanco=blanco,
    )

    # Las entradas pueden estar dentro de 'mt' o al nivel raiz.
    entradas = mt.get("inputs", documento.get("inputs", []))
    return maquina, [_texto(e) for e in entradas]
