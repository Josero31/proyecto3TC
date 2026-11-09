Proyecto 3 - Simulador de Maquinas de Turing
Ángel  Mérida - 23661 José Sánchez – 231221
Teoria de la Computacion, Universidad del Valle de Guatemala

Simulador de Maquinas de Turing (MT) de una cinta con memoria en el estado.
Lee la descripcion formal de la MT desde un archivo YAML, simula cada cadena
de entrada, muestra todas las descripciones instantaneas (IDs) e indica si la
cadena es aceptada o rechazada junto con la configuracion final de la cinta.


Requisitos

Python 3.9 o superior y PyYAML.

    pip install -r requirements.txt


Ejecucion

Sin argumentos se simulan todas las maquinas de la carpeta maquinas/:

    python main.py

Tambien se puede indicar una o varias maquinas especificas:

    python main.py maquinas/reconocedora_ww.yaml
    python main.py maquinas/alteradora_ordenamiento.yaml
    python main.py maquinas/alteradora_multiplicacion.yaml

Opciones:

    --salida archivo.txt   guarda la salida completa en un archivo
    --max-pasos N          limite de pasos por cadena (por defecto 100000)


Formato del archivo YAML

    mt:
      states: [q0, q1, qf]
      input_alphabet: [a, b]
      tape_alphabet: [a, b, B]
      initial_state: q0
      accept_states: [qf]
      transitions:
        - state: q0
          read: [a, B]
          write: [a, B]
          move: R
          next: q1
      inputs:
        - "ab"

En cada transicion, read es [simbolo leido en la cinta, simbolo en memoria] y
write es [nuevo simbolo en memoria, simbolo escrito en la cinta]. La transicion
anterior corresponde a d([q0, B], a) = ([q1, a], B, R). Los movimientos validos
son L, R y S. El simbolo blanco es B. Tambien se aceptan transiciones en una
sola linea, por ejemplo:

    - {state: q0, read: [a, B], write: [a, B], move: R, next: q1}


Arquitectura

    main.py          punto de entrada; lee argumentos, ejecuta y muestra resultados
    parser_yaml.py   parsing del YAML y construccion de la MT
    maquina.py       estructuras Transicion y MaquinaTuring, validacion y delta
    cinta.py         cinta infinita, parsing de la entrada y formato de las IDs
    simulador.py     algoritmo de simulacion paso a paso
    maquinas/        archivos YAML de las maquinas del proyecto (una reconocedora y dos alteradoras)

Flujo: parser_yaml.cargar() convierte cada transicion en un objeto Transicion
y crea la MaquinaTuring, que valida estados, alfabetos, movimientos y
determinismo. La funcion de transicion se guarda en un diccionario con clave
(estado, memoria, simbolo leido). La cinta es un diccionario posicion ->
simbolo, por lo que crece en ambas direcciones sin limite. simulador.simular()
parte de [q0, B] con el cabezal en el primer simbolo, aplica transiciones hasta
que no existe ninguna aplicable y registra la ID de cada paso con la forma
alfa [q, m] beta, donde el cabezal esta sobre el primer simbolo de beta. La
cadena se acepta si la MT se detiene en un estado de aceptacion.


MT reconocedora: L = { ww | w en {a, b}+ }

Archivo: maquinas/reconocedora_ww.yaml. Lenguaje no libre de contexto.
8 estados y 33 transiciones.

Fase 1 (q0 a q3): marca alternadamente el primer simbolo sin marcar de la
izquierda (a -> x, b -> y) y el ultimo de la derecha (a -> X, b -> Y) hasta
encontrar la mitad. Si la longitud es impar, q2 no encuentra simbolo que
marcar y la cadena se rechaza.

Fase 2 (q4 a q6): guarda en memoria el primer simbolo pendiente de la primera
mitad, lo tacha con Z, busca el primer simbolo pendiente de la segunda mitad y
lo compara con la memoria. Si coinciden lo tacha y regresa; si no, la MT se
detiene en q6 y rechaza. Si ya no quedan pendientes, acepta en qf.

Cadenas de prueba: abaaba, abbabb, babbbabb (aceptadas); ababb, abbaab, aabbab
(rechazadas).


MT alteradora: ordenamiento de cadenas sobre {a, b, c}

Archivo: maquinas/alteradora_ordenamiento.yaml. Ejemplo: cabac -> aabcc.
5 estados y 27 transiciones.

q0 recorre la cinta guardando en memoria el simbolo anterior. Al encontrar
una inversion (ba, ca o cb) escribe el simbolo mayor en la celda actual, guarda
el menor y retrocede (q1), que escribe el menor en la celda anterior. q2
regresa al inicio para un nuevo recorrido. Cuando q0 llega al final sin
inversiones, q3 regresa el cabezal al inicio y la MT termina en qf.

Cadenas de prueba: cabac, ccbbaa, bcaacb, abcabc, cbacba.


MT alteradora 2: multiplicacion unaria

Archivo: maquinas/alteradora_multiplicacion.yaml. Entrada 1^a # 1^b con a, b >= 1;
la cinta final es 1^(a*b). Ejemplo: 111#11 -> 111111.
12 estados y 38 transiciones.

Por cada 1 de a (marcado con X) copia completa la cadena b al final de la cinta,
en una zona de resultado separada por $. Cada 1 de b se marca con Y mientras se
copia y luego se restaura a 1. Al terminar, q8 a q10 borran a, #, b y $, y la MT
acepta en qf con solo el resultado en la cinta. Las entradas sin # o sin 1 en
alguno de los lados se rechazan. Esta maquina no necesita la memoria del estado
(siempre es B).

Cadenas de prueba: 111#11, 11#1111, 1111#111, 11111#11 (aceptadas); 111# y 1111
(rechazadas).


Verificacion

Las tres maquinas se probaron de forma exhaustiva, sin errores:

- Reconocedora: todas las cadenas sobre {a, b} de longitud 0 a 10, comparando
  con la definicion del lenguaje.
- Alteradora de ordenamiento: todas las cadenas sobre {a, b, c} de longitud 0
  a 8, comparando con el ordenamiento esperado.
- Alteradora de multiplicacion: todas las combinaciones 1^a # 1^b con a, b de
  1 a 8, comparando con 1^(a*b).
