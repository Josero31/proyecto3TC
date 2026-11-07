"""
Simulacion de la MT sobre una cadena de entrada.
"""

from dataclasses import dataclass, field

from cinta import Cinta, tokenizar


@dataclass
class Resultado:
    entrada: str
    aceptada: bool
    motivo: str
    cinta_final: str
    pasos: int
    ids: list = field(default_factory=list)


def simular(maquina, entrada, max_pasos=100000):
    """
    Ejecuta la MT desde la configuracion inicial [q0, B] con el cabezal en
    el primer simbolo de la entrada. Se detiene cuando no existe transicion
    aplicable; la cadena se acepta si el estado final es de aceptacion.
    """
    try:
        simbolos = tokenizar(entrada, maquina.alfabeto_entrada)
    except ValueError as error:
        return Resultado(entrada, False, f"Entrada invalida: {error}",
                         entrada, 0)

    cinta = Cinta(simbolos, maquina.blanco)
    estado = maquina.estado_inicial
    memoria = maquina.blanco
    ids = [cinta.descripcion_instantanea(estado, memoria)]
    pasos = 0

    while True:
        simbolo = cinta.leer()
        t = maquina.transicion(estado, memoria, simbolo)
        if t is None:
            break
        if pasos >= max_pasos:
            return Resultado(entrada, False,
                             f"Se alcanzo el limite de {max_pasos} pasos",
                             cinta.contenido(), pasos, ids)
        cinta.escribir(t.escribe_cinta)
        cinta.mover(t.movimiento)
        estado = t.siguiente
        memoria = t.escribe_memoria
        pasos += 1
        ids.append(cinta.descripcion_instantanea(estado, memoria))

    if estado in maquina.estados_aceptacion:
        motivo = f"La MT se detuvo en el estado de aceptacion {estado}"
        aceptada = True
    else:
        motivo = (f"La MT se detuvo en {estado}: no existe "
                  f"δ([{estado}, {memoria}], {simbolo}) y {estado} "
                  f"no es estado de aceptacion")
        aceptada = False
    return Resultado(entrada, aceptada, motivo, cinta.contenido(), pasos, ids)
