---
titulo: Fuente variable 0–30 V / 3 A
proposito: Fuente de banco con regulación lineal y transistor de paso, ajustable con un potenciómetro.
categoria: alimentacion
etiquetas: [banco, laboratorio, lineal]

dificultad:
  componentes: 1
  montaje: 2
  instrumentacion: 1
  programacion: 0
  riesgo_electrico: 2
  calibracion: 2

tiempo:
  horas_min: 6
  horas_max: 9
  sesiones: 3
  perfil: ha soldado antes y sabe usar un multímetro

seguridad:
  red_electrica: true
  advertencias: [capacitores-cargados, superficie-caliente]

conceptos:
  - slug: regulacion-lineal
    nota: El LM317 disipa como calor la diferencia entre la tensión rectificada y la de salida — por eso hace falta un buen disipador en el transistor de paso.
  - slug: realimentacion
    nota: El LM317 compara internamente su salida contra una referencia de 1,25 V y ajusta su conducción para mantenerla estable pese a variaciones de carga.
  - slug: disipacion-termica
    nota: A corriente alta, casi toda la potencia disipada la asume el 2N3055 externo, no el LM317 — de ahí el disipador TO-3.
  - slug: ley-de-ohm
    nota: R1 y el potenciómetro fijan el voltaje de salida según Vout = 1,25 V × (1 + R2/R1).

materiales:
  - ref: LM317T
    cantidad: 1
  - ref: 2N3055
    cantidad: 1
  - ref: TRAFO-24V-3A
    cantidad: 1
  - ref: PUENTE-RECTIFICADOR-4A
    cantidad: 1
  - ref: CAP-ELECTROLITICO-2200UF-50V
    cantidad: 1
  - ref: CAP-ELECTROLITICO-1UF-50V
    cantidad: 1
  - ref: RES-CARBON-1-4W
    cantidad: 3
    nota: R1 (240 Ω), resistencia de sensado y una de arranque
  - ref: POT-5K-LINEAL
    cantidad: 1
  - ref: DISIPADOR-TO3
    cantidad: 1
  - ref: PORTAFUSIBLE-CHASIS
    cantidad: 1
  - ref: BORNERAS-BANANA-PAR
    cantidad: 1
  - ref: CHASIS-METALICO-PEQUENO
    cantidad: 1
  - ref: PERFBOARD-5X7
    cantidad: 1

herramientas: ["Cautín y estaño", "Multímetro", "Taladro (para perforar el chasis)", "Juego de destornilladores"]

imagenes:
  - alt: Vista general de la fuente terminada, con el potenciómetro y las borneras en el panel frontal
  - alt: Interior del chasis mostrando el transformador, el perfboard y el disipador del 2N3055
  - alt: Multímetro midiendo la tensión de salida durante la prueba de rango

diagramas:
  - titulo: Esquemático completo — rectificador, LM317 y transistor de paso
    alt: Diagrama del rectificador de puente, el LM317 con red de ajuste y el 2N3055 como transistor de paso externo

pasos:
  - titulo: Arma el rectificador y el filtro
    contenido: Monta el puente rectificador a la salida del secundario del transformador y el capacitor electrolítico de 2200 µF a su salida, respetando la polaridad.
    verificacion: Con el transformador desconectado de la red, mide con el multímetro en modo diodo que el puente conduce en el sentido esperado en sus cuatro terminales.
  - titulo: Monta el LM317 con su red de ajuste
    contenido: Coloca el LM317 en el perfboard con R1 entre la salida y el pin ADJ, y el potenciómetro entre ADJ y tierra. Agrega el capacitor de 1 µF entre ADJ y tierra para estabilidad.
    verificacion: Antes de conectar el 2N3055, alimenta solo el LM317 y confirma que el voltaje de salida cambia al girar el potenciómetro.
  - titulo: Agrega el transistor de paso 2N3055
    contenido: Monta el 2N3055 sobre el disipador TO-3 y conéctalo como transistor de paso externo al LM317 para soportar hasta 3 A.
    verificacion: Con una carga resistiva de prueba, confirma que el disipador no llega a una temperatura que no puedas sostener con la mano por unos segundos.
  - titulo: Cierra el chasis y prueba con carga
    contenido: Fija el transformador, el perfboard, el potenciómetro y las borneras al chasis. Conecta el portafusible en serie con la línea de entrada.
    verificacion: Con el multímetro en las borneras de salida, verifica que el rango de ajuste cubre aproximadamente de 1,5 V a 28 V sin carga.

resultados:
  - parametro: Rango de tensión de salida
    esperado: "≈1,5 V a 28 V, ajustable con el potenciómetro"
  - parametro: Rizado en la salida a plena carga
    esperado: "Menor a 100 mV pico a pico con el filtro propuesto"
  - parametro: Regulación de línea
    esperado: "Variación de salida menor al 1 % ante cambios normales de la red"

fallas:
  - sintoma: La salida no baja de un voltaje mínimo alto (≈5 V) aunque gires el potenciómetro al mínimo
    causas:
      - Potenciómetro conectado con dos terminales invertidas
      - R1 con un valor mucho mayor al indicado
  - sintoma: El 2N3055 se calienta excesivamente incluso sin carga conectada
    causas:
      - Conexión errónea del transistor de paso respecto al LM317
      - Resistencia de sensado de valor incorrecto
  - sintoma: Rizado alto y notorio en la salida
    causas:
      - Capacitor de filtro de menor capacitancia a la indicada
      - Mala conexión a tierra entre el rectificador y el regulador

notas_colaborador: >
  Este proyecto es contenido de ejemplo para probar la estructura de datos del sitio — todavía no
  se ha montado ni verificado físicamente. Reemplázalo por un proyecto real siguiendo
  PLANTILLA-PROYECTO.md antes de publicar el sitio.

estado: borrador
probado_por: []
actualizado: 2026-08-16
licencia: CC-BY-SA-4.0
---

Una fuente de banco ajustable es la primera herramienta que vale la pena construir en vez de
comprar: cubre casi cualquier proyecto de baja potencia que hagas después, y te obliga a entender
regulación lineal, disipación térmica y filtrado de rizado — tres conceptos que se repiten en la
mitad de los circuitos de este sitio.

Con este proyecto aprendes a diseñar la red de resistencias que fija el voltaje de un LM317, a
extender su corriente con un transistor de paso externo, y a verificar con un multímetro que un
regulador está funcionando dentro de su rango antes de confiarle una carga real.

Lo que **no** hace: no tiene protección electrónica contra cortocircuito más allá del fusible de
entrada, ni indicador digital de voltaje o corriente — son mejoras razonables para una segunda
versión, no parte de este montaje base.
