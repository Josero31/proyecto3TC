"""
Cinta infinita en ambas direcciones y descripciones instantaneas (IDs).
"""


def tokenizar(cadena, alfabeto):
    """
    Convierte la cadena de entrada en una lista de simbolos del alfabeto.
    Usa coincidencia mas larga, asi soporta simbolos de mas de un caracter.
    Lanza ValueError si encuentra un simbolo que no pertenece al alfabeto.
    """
    simbolos = sorted(alfabeto, key=len, reverse=True)
    resultado = []
    i = 0
    while i < len(cadena):
        if cadena[i].isspace():
            i += 1
            continue
        for s in simbolos:
            if cadena.startswith(s, i):
                resultado.append(s)
                i += len(s)
                break
        else:
            raise ValueError(
                f"el simbolo '{cadena[i]}' (posicion {i}) no pertenece "
                f"al alfabeto de entrada")
    return resultado


class Cinta:
    """
    Cinta representada como diccionario posicion -> simbolo.
    Las celdas que no estan en el diccionario contienen el blanco, por lo
    que la cinta crece libremente hacia la izquierda y la derecha.
    """

    def __init__(self, simbolos, blanco):
        self.blanco = blanco
        self.celdas = {i: s for i, s in enumerate(simbolos)}
        self.cabezal = 0

    def leer(self):
        return self.celdas.get(self.cabezal, self.blanco)

    def escribir(self, simbolo):
        if simbolo == self.blanco:
            self.celdas.pop(self.cabezal, None)
        else:
            self.celdas[self.cabezal] = simbolo

    def mover(self, movimiento):
        if movimiento == "L":
            self.cabezal -= 1
        elif movimiento == "R":
            self.cabezal += 1

    def _rango(self, incluir_cabezal):
        posiciones = set(self.celdas)
        if incluir_cabezal:
            posiciones.add(self.cabezal)
        if not posiciones:
            return None
        return min(posiciones), max(posiciones)

    def _unir(self, simbolos):
        # Si todos los simbolos son de un caracter se escriben pegados.
        separador = "" if all(len(s) == 1 for s in simbolos) else " "
        return separador.join(simbolos)

    def contenido(self):
        """Contenido de la cinta sin los blancos de los extremos."""
        rango = self._rango(incluir_cabezal=False)
        if rango is None:
            return self.blanco
        inicio, fin = rango
        return self._unir([self.celdas.get(i, self.blanco)
                           for i in range(inicio, fin + 1)])

    def descripcion_instantanea(self, estado, memoria):
        """
        ID en la forma  alfa [q, m] beta, donde el cabezal esta sobre el
        primer simbolo de beta.
        """
        inicio, fin = self._rango(incluir_cabezal=True)
        izquierda = [self.celdas.get(i, self.blanco)
                     for i in range(inicio, self.cabezal)]
        derecha = [self.celdas.get(i, self.blanco)
                   for i in range(self.cabezal, fin + 1)]
        partes = []
        if izquierda:
            partes.append(self._unir(izquierda))
        partes.append(f"[{estado}, {memoria}]")
        partes.append(self._unir(derecha))
        return " ".join(partes)
