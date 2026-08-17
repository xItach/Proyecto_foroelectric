<!--
  Plantilla para un proyecto nuevo.

  1. Copia este archivo a:
       src/content/proyectos/<categoria>/<slug-del-proyecto>.md
     donde <categoria> es una de: control, alimentacion, potencia,
     audiovisuales, entretenimiento — y <slug-del-proyecto> es el nombre
     del archivo en minúsculas y con guiones (sin espacios ni tildes).

  2. Llena todos los campos. Si el sitio está corriendo (`npm run dev`),
     cualquier campo obligatorio que falte o esté mal escrito rompe el build
     y te dice exactamente cuál — es la validación automática de la que
     habla docs/anteproyecto.html §13.

  3. Antes de publicar (estado: publicado), el proyecto debe estar
     físicamente montado y probado por quien lo sube. No subas "publicado"
     sin haberlo armado — para eso existe "borrador" y "revision".

  4. Todo `ref:` en materiales debe existir como `id:` en
     src/content/componentes.yaml — si no existe, agrégalo ahí primero (con
     su precio en COP y la fecha de hoy en `verificado`).

  5. Todo `slug:` en conceptos debe existir como `id:` en
     src/content/conceptos.yaml — si el concepto no está, agrégalo ahí
     primero con su explicación general (la teoría va allá, no aquí).

  Borra este bloque de comentario antes de guardar el archivo real.
-->
---
titulo: Nombre del proyecto
proposito: Una sola línea — qué hace y qué se aprende al construirlo.
categoria: control # control | alimentacion | potencia | audiovisuales | entretenimiento
etiquetas: []

# Rúbrica de dificultad — puntúa cada eje de 0 a 2. El nivel 1-5 se calcula
# solo, no lo escribas a mano. Ver docs/anteproyecto.html §4.
dificultad:
  componentes: 0 # 0: <15 · 1: 15-40 · 2: >40
  montaje: 0 # 0: protoboard · 1: perfboard/PCB · 2: SMD o mecanizado de caja
  instrumentacion: 0 # 0: ninguna · 1: multímetro · 2: osciloscopio/generador
  programacion: 0 # 0: no lleva · 1: firmware listo · 2: hay que escribir código
  riesgo_electrico: 0 # 0: hasta 24V DC · 1: litio o >1A · 2: red eléctrica
  calibracion: 0 # 0: funciona al conectar · 1: un ajuste simple · 2: caracterización

tiempo:
  horas_min: 1
  horas_max: 2
  sesiones: 1
  perfil: "a quién le toma este tiempo, ej: no necesita experiencia previa"

seguridad:
  red_electrica: false # true si conecta a 120/240V — dispara el aviso automáticamente
  advertencias: [] # ver opciones en src/data/advertencias.ts

# Enlaza al glosario en vez de repetir la teoría. La `nota` es solo cómo se
# aplica ESTE concepto en ESTE circuito puntual (2-3 líneas).
conceptos: []
# - slug: ley-de-ohm
#   nota: "..."

materiales: []
# - ref: NE555
#   cantidad: 1
#   nota: "opcional"

herramientas: [] # se compran una vez, no entran al costo del proyecto

apoyo: [] # enlaces externos, PDFs, videos — para profundizar después
# - titulo: "Datasheet NE555"
#   url: "https://..."
#   tipo: datasheet # enlace | pdf | video | datasheet

imagenes: [] # deja `src` vacío si aún no tienes la foto — se muestra un placeholder honesto
# - alt: "Descripción de la foto"
#   src: "/imagenes/proyectos/mi-proyecto/01.jpg"

diagramas: []
# - titulo: "Esquemático completo"
#   alt: "Descripción del diagrama"
#   src: "/imagenes/proyectos/mi-proyecto/diagrama.svg"

# Por etapas, cada una con un punto de verificación medible cuando aplique.
# Esto es lo que separa una guía de un álbum de fotos.
pasos: []
# - titulo: "Arma el oscilador"
#   contenido: "..."
#   verificacion: "Antes de seguir, debes leer 12V ± 0.5 en el pin 3."

resultados: [] # valores medibles, no solo "funciona"
# - parametro: "Tensión de salida"
#   esperado: "..."

fallas: [] # síntoma -> causas probables, en orden de probabilidad
# - sintoma: "No enciende"
#   causas: ["...", "..."]

notas_colaborador: "" # contexto libre: por qué este diseño, qué cambiarías, etc.

estado: borrador # borrador | revision | publicado | obsoleto
probado_por: [] # tu nombre, una vez lo hayas armado y probado
actualizado: 2026-08-16
licencia: CC-BY-SA-4.0
---

Introducción del proyecto: qué hace, qué se aprende al construirlo y — sobre todo — qué **no**
hace. Los límites declarados evitan la mitad de las decepciones (ver docs/anteproyecto.html §5).
