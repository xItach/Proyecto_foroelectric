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
formato IEEE. Ajustes en el bloque 1 de `main.tex`:

- `\altologo` — alto del logo (por defecto 15 mm).
- `\margensuplogo` — distancia al borde superior del papel (7 mm).
- `\margenlatlogo` — distancia al borde lateral (18 mm).
- `\bajartitulo` — espacio extra sobre el título para que no choque con el
  logo (8 mm). Ponlo en `0mm` si tu logo es pequeño.

Si el logo es muy ancho se comerá el espacio del texto institucional: baja
`\altologo` o cambia el `0.60\anchoencabezado` del `\parbox` por un valor
menor. Si tu bloque de texto necesita más líneas, cámbialo a `\tiny`.

Para pasar el logo a la derecha y el texto institucional a la izquierda,
intercambia `\cajalogo` y el `\parbox` dentro del `minipage` de
`\encabezadoinstitucional` (y cambia `\raggedleft` por `\raggedright`).
El encabezado solo se dibuja en la primera página, que es lo que pide el
estilo IEEE.

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
- **`Overfull \hbox`** — es un aviso, no un error. Solo importa si ves texto
  saliéndose de la columna.
- **El logo pisa el título** — sube el valor de `\bajartitulo` o baja
  `\altologo`.
