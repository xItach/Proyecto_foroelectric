# Informe IEEE — Simulación en CADe SIMU

Plantilla LaTeX en formato IEEE (clase `IEEEtran`) para el informe de la
simulación de un diagrama ladder en CADe SIMU. Pensada para tres autores y
con espacio para el logo institucional en el margen superior de la primera
página.

## Subirlo a Overleaf

1. Comprime la carpeta `informe/` en un `.zip`.
2. En Overleaf: **New Project → Upload Project** y suelta el `.zip`.
3. **Menu → Compiler → pdfLaTeX** (no LuaLaTeX ni XeLaTeX: la plantilla usa
   `inputenc`).
4. **Menu → Main document → `main.tex`**.
5. Compila. Debe salir el PDF aunque todavía no hayas subido ninguna imagen:
   el logo y las figuras que falten aparecen como recuadros de reserva.

> Alternativa sin zip: crea un proyecto en blanco, pega el contenido de
> `main.tex`, crea `referencias.bib` y una carpeta `figuras/`.

## Qué editar (en este orden)

| Dónde | Qué |
|---|---|
| Bloque **1. DATOS INSTITUCIONALES** de `main.tex` | Universidad, facultad, programa, asignatura. |
| `\title{...}` y `\author{...}` | Título real y los tres integrantes con código y correo. |
| `figuras/` | Logo y capturas (ver `figuras/LEEME.md`). |
| Cuerpo del documento | Todo lo que está marcado **[entre corchetes en negrita]**. |
| `referencias.bib` | Verifica los datos y borra lo que no cites. |

Los comentarios `%` dentro de `main.tex` explican qué debe responder cada
sección; son invisibles en el PDF, así que puedes dejarlos.

## El logo del margen superior

Se coloca con `eso-pic`, **sin** mover el área de texto, así que no rompe el
formato IEEE. Solo aparece en la primera página.

El bloque (logo + datos de la universidad) **se mide al compilar** y el título
baja automáticamente lo necesario para dejar `\holguratitulo` de aire debajo
del encabezado. Es decir: puedes cambiar el alto del logo o quitar y agregar
líneas de texto institucional sin que nada se solape ni tengas que cuadrar
milímetros a mano.

Ajustes disponibles, todos en el bloque 1 de `main.tex`:

- `\altologo` — alto del logo (13 mm por defecto).
- `\margensuplogo` — distancia al borde superior del papel (6 mm).
- `\margenlatlogo` — distancia a los bordes laterales (18 mm).
- `\holguratitulo` — separación entre el encabezado y el título (5 mm).
  **Si lo ves apretado, sube este valor**: es el único que hay que tocar.

Las líneas del texto institucional se editan en `\textoinstitucional`
(bloque 2); si te queda largo, cámbialo de `\scriptsize` a `\tiny`. El ancho
del texto se calcula solo a partir de lo que ocupe el logo, así que un logo
ancho no lo pisa.

Para pasar el logo a la derecha y el texto a la izquierda, intercambia los dos
`\parbox` del paso 4 de `\encabezadoinstitucional` y cambia `\raggedleft`
por `\raggedright`.

## Estructura del informe

| Sección | Qué resuelve |
|---|---|
| Resumen / Abstract | Qué se simuló, cómo se verificó y qué resultó. Se escribe al final. |
| I. Introducción | Contexto, problema, por qué simular antes de cablear, mapa del documento. |
| II. Objetivos | General + específicos. Cada específico debe tener después su conclusión. |
| III. Marco teórico | Solo la teoría que se usa después: ladder, elementos, enclavamientos, temporizadores, CADe SIMU. |
| IV. Materiales y software | Tabla de elementos con su designación (KM1, F1…) + versión del simulador. |
| V. Descripción del proceso | Enunciado redactado por ustedes + **requisitos numerados R1…Rn**. |
| VI. Desarrollo | Asignación de E/S → ecuaciones booleanas → circuito de fuerza → ladder → procedimiento seguido. |
| VII. Pruebas y resultados | Protocolo que prueba R1…Rn uno por uno, capturas por estado, diagrama de tiempos. Solo lo observado. |
| VIII. Análisis | Interpretación, errores encontrados y corregidos, límites del simulador. |
| IX. Conclusiones | Una por objetivo específico. |
| X. Recomendaciones | Opcional. |
| Apéndices | Aportes de cada integrante y archivos `.dsm` anexos. |

La idea que sostiene la segmentación: los **requisitos numerados** de la
sección V son las mismas filas de la tabla de pruebas de la sección VII. Eso
hace que el informe se verifique solo y evita el error típico de mostrar
capturas sin decir qué demuestran.

## Problemas frecuentes

- **Recuadros que dicen «Falta la imagen»** — es normal hasta que subas esa
  captura. Las figuras se insertan con `\imagen{ancho}{archivo}`, que dibuja
  un recuadro en vez de detener la compilación cuando el archivo no existe.
- **Las citas salen como `[?]`** — compila dos veces (Overleaf lo hace solo al
  volver a pulsar *Recompile*); BibTeX necesita una segunda pasada.
- **Una imagen se sale de la página o no se centra** — el ancho que le pasas
  a `\imagen` es mayor que el área de texto. Máximo `\columnwidth` en una
  figura de una columna y `\textwidth` en una `figure*`. Si la captura se ve
  pequeña a ese ancho, el problema es la resolución del PNG, no el ancho:
  vuelve a capturarla con más zoom en CADe SIMU.

- **`Overfull \hbox`** — es un aviso, no un error. Solo importa si ves texto
  saliéndose de la columna.
- **El título queda muy pegado (o muy lejos) del encabezado** — es el único
  ajuste fino que queda: sube o baja `\holguratitulo`. No toques
  `\bajartitulo`, que ahora se calcula solo.
