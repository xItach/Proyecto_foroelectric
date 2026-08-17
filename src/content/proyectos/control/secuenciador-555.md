---
titulo: Secuenciador de LEDs con 555
proposito: Primer proyecto con temporizador — astable, cálculo de frecuencia y verificación con multímetro.
categoria: control
etiquetas: [principiante, protoboard]

dificultad:
  componentes: 0
  montaje: 0
  instrumentacion: 0
  programacion: 0
  riesgo_electrico: 0
  calibracion: 1

tiempo:
  horas_min: 1
  horas_max: 2
  sesiones: 1
  perfil: no necesita experiencia previa

seguridad:
  red_electrica: false
  advertencias: []

conceptos:
  - slug: astable
    nota: El 555 en modo astable es lo que genera los pulsos que encienden y apagan los LED sin ningún disparo externo.
  - slug: constante-rc
    nota: R1, R2 y C1 fijan la frecuencia del parpadeo — cambiar cualquiera de los tres cambia la velocidad de la secuencia.
  - slug: ley-de-ohm
    nota: Cada resistencia en serie con un LED se calcula con la ley de Ohm para no exceder su corriente máxima.

materiales:
  - ref: NE555
    cantidad: 1
  - ref: LED-5MM-ROJO
    cantidad: 4
  - ref: RES-CARBON-1-4W
    cantidad: 6
    nota: 2 para el temporizador (R1, R2), 4 limitadoras para los LED
  - ref: CAP-CERAMICO-100NF
    cantidad: 1
  - ref: PROTOBOARD-830
    cantidad: 1
  - ref: CABLES-JUMPER-M-M
    cantidad: 1

herramientas: []

imagenes:
  - alt: Vista general de la protoboard con el 555 y los cuatro LED montados
  - alt: Detalle del cableado del oscilador alrededor del temporizador 555
  - alt: Circuito encendido, con los LED parpadeando en secuencia

diagramas:
  - titulo: Esquemático del secuenciador
    alt: Diagrama del 555 en modo astable con cuatro LED en la salida

pasos:
  - titulo: Arma el oscilador astable
    contenido: Conecta R1 y R2 en serie entre el pin 7 (descarga) y el pin 8 (Vcc). Une el punto medio de R1 y R2 al pin 2 (disparo) y al pin 6 (umbral). C1 va del pin 2 a tierra.
    verificacion: Con el multímetro en modo continuidad, confirma que el pin 2 y el pin 6 quedaron unidos entre sí.
  - titulo: Conecta la salida a los LED
    contenido: Del pin 3 (salida) sale una resistencia limitadora en serie con cada LED hacia tierra, los cuatro en paralelo entre sí.
    verificacion: Con la fuente aún desconectada, revisa que cada LED tenga su propia resistencia en serie antes de energizar.
  - titulo: Alimenta el circuito
    contenido: Conecta 9 V al pin 8 y tierra al pin 1. Los LED deberían empezar a parpadear de inmediato.
    verificacion: Deberías ver un parpadeo visible a simple vista; con osciloscopio, una onda cuadrada de aproximadamente 1–2 Hz en el pin 3.

resultados:
  - parametro: Frecuencia de parpadeo
    esperado: "≈1–2 Hz con los valores de R1, R2 y C1 propuestos"
  - parametro: Tensión en el pin 3 (nivel alto)
    esperado: "≈ Vcc − 1,5 V mientras el LED correspondiente está encendido"

fallas:
  - sintoma: Los LED no encienden
    causas:
      - Polaridad invertida del LED
      - Pin 4 (reset) no conectado a Vcc
      - Batería agotada o mal conectada
  - sintoma: El parpadeo es demasiado rápido o lento para verlo a simple vista
    causas:
      - Valor de R1, R2 o C1 distinto al indicado
      - C1 con fugas o de valor incorrecto

notas_colaborador: >
  Este proyecto es contenido de ejemplo para probar la estructura de datos del sitio — todavía no
  se ha montado ni verificado físicamente. Reemplázalo por un proyecto real siguiendo
  PLANTILLA-PROYECTO.md antes de publicar el sitio.

estado: borrador
probado_por: []
actualizado: 2026-08-16
licencia: CC-BY-SA-4.0
---

Un secuenciador de LEDs con el temporizador 555 es, para casi cualquiera que empieza en
electrónica, el primer circuito que hace algo visible sin depender de un microcontrolador. El 555
configurado en modo astable genera una señal cuadrada continua; esa señal enciende y apaga cuatro
LED, dando la sensación de secuencia.

Con este proyecto aprendes a leer un datasheet lo suficiente para identificar los pines que
importan, a calcular resistencias limitadoras con la ley de Ohm, y a verificar con un multímetro
que un cableado está bien antes de energizarlo — el hábito más útil que te vas a llevar.

Lo que **no** hace: no controla la secuencia de forma independiente por LED (los cuatro parpadean
juntos, al mismo tiempo, no en cadena), y no tiene ningún control de brillo. Para una secuencia
LED por LED hace falta un contador digital o un microcontrolador — un proyecto distinto, de mayor
dificultad.
