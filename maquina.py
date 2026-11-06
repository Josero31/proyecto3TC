"""
Estructuras de datos de la Maquina de Turing de una cinta.

Cada estado de la MT lleva asociado un simbolo de memoria (almacenamiento
en el control finito), por lo que una configuracion del control es el par
[q, m]. Una transicion tiene la forma:

    delta([q, m], s) = ([p, m'], s', D)

donde q es el estado actual, m el simbolo en memoria, s el simbolo leido
en la cinta, p el siguiente estado, m' el nuevo simbolo en memoria, s' el
simbolo que se escribe en la cinta y D el movimiento del cabezal (L, R, S).
"""

from dataclasses import dataclass

BLANCO_POR_DEFECTO = "B"
MOVIMIENTOS = ("L", "R", "S")


class ErrorConfiguracion(Exception):
    """Error en la descripcion formal de la MT."""


@dataclass(frozen=True)
class Transicion:
    estado: str
    lee_cinta: str
    lee_memoria: str
    escribe_memoria: str
    escribe_cinta: str
    movimiento: str
    siguiente: str

    def formal(self):
        """Representacion en notacion delta([q, m], s) = ([p, m'], s', D)."""
        return (f"δ([{self.estado}, {self.lee_memoria}], {self.lee_cinta}) = "
                f"([{self.siguiente}, {self.escribe_memoria}], "
                f"{self.escribe_cinta}, {self.movimiento})")


class MaquinaTuring:
    """Descripcion formal M = (Q, Sigma, Gamma, delta, q0, B, F)."""

    def __init__(self, estados, alfabeto_entrada, alfabeto_cinta,
                 estado_inicial, estados_aceptacion, transiciones,
                 blanco=BLANCO_POR_DEFECTO):
        self.estados = list(estados)
        self.alfabeto_entrada = list(alfabeto_entrada)
        self.alfabeto_cinta = list(alfabeto_cinta)
        self.estado_inicial = estado_inicial
        self.estados_aceptacion = set(estados_aceptacion)
        self.blanco = blanco
        self.transiciones = list(transiciones)

        # La funcion de transicion se guarda como diccionario:
        # (estado, memoria, simbolo_leido) -> Transicion
        self.delta = {}
        self._validar()

    def _validar(self):
        estados = set(self.estados)
        cinta = set(self.alfabeto_cinta)

        if self.estado_inicial not in estados:
            raise ErrorConfiguracion(
                f"El estado inicial '{self.estado_inicial}' no esta en states")
        for f in self.estados_aceptacion:
            if f not in estados:
                raise ErrorConfiguracion(
                    f"El estado de aceptacion '{f}' no esta en states")
        if self.blanco not in cinta:
            raise ErrorConfiguracion(
                f"El simbolo blanco '{self.blanco}' debe estar en tape_alphabet")
        if self.blanco in self.alfabeto_entrada:
            raise ErrorConfiguracion(
                "El simbolo blanco no puede pertenecer a input_alphabet")
        for s in self.alfabeto_entrada:
            if s not in cinta:
                raise ErrorConfiguracion(
                    f"El simbolo de entrada '{s}' no esta en tape_alphabet")

        for t in self.transiciones:
            for q in (t.estado, t.siguiente):
                if q not in estados:
                    raise ErrorConfiguracion(
                        f"Estado desconocido '{q}' en {t.formal()}")
            for s in (t.lee_cinta, t.lee_memoria,
                      t.escribe_cinta, t.escribe_memoria):
                if s not in cinta:
                    raise ErrorConfiguracion(
                        f"Simbolo desconocido '{s}' en {t.formal()}")
            if t.movimiento not in MOVIMIENTOS:
                raise ErrorConfiguracion(
                    f"Movimiento invalido '{t.movimiento}' en {t.formal()}")

            clave = (t.estado, t.lee_memoria, t.lee_cinta)
            if clave in self.delta:
                raise ErrorConfiguracion(
                    "La MT no es determinista, hay dos transiciones para "
                    f"δ([{t.estado}, {t.lee_memoria}], {t.lee_cinta})")
            self.delta[clave] = t

    def transicion(self, estado, memoria, simbolo):
        """Devuelve la transicion aplicable o None si no existe."""
        return self.delta.get((estado, memoria, simbolo))

    def descripcion(self):
        """Texto con la descripcion formal completa de la MT."""
        lineas = [
            f"Q  = {{{', '.join(self.estados)}}}",
            f"Σ  = {{{', '.join(self.alfabeto_entrada)}}}",
            f"Γ  = {{{', '.join(self.alfabeto_cinta)}}}",
            f"q0 = {self.estado_inicial}",
            f"B  = {self.blanco}",
            f"F  = {{{', '.join(sorted(self.estados_aceptacion))}}}",
            f"Funciones de transicion ({len(self.transiciones)}):",
        ]
        lineas += [f"  {t.formal()}" for t in self.transiciones]
        return "\n".join(lineas)
