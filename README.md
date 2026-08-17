# Foro Electric

Guías de montaje electrónico por categoría (Control, Alimentación, Potencia, Audiovisuales,
Entretenimiento), con dificultad calculada por rúbrica, costos en COP derivados de un catálogo
compartido, y una página de detalle pensada para evaluar, comprar, construir y depurar un
proyecto. El razonamiento completo detrás de estas decisiones está en
[`docs/anteproyecto.html`](docs/anteproyecto.html).

Este es el **esqueleto**: la estructura, el esquema de datos y las páginas están completos y
funcionando con dos proyectos de ejemplo (marcados `estado: borrador`, sin fotos reales). El
proyecto piloto real se agrega después, siguiendo `PLANTILLA-PROYECTO.md`.

## Stack

- **[Astro](https://astro.build)** — sitio estático, sin servidor que mantener.
- **Content Collections** (`src/content/`) — cada proyecto es un archivo Markdown con
  metadatos validados; si falta un campo obligatorio, el build falla y dice cuál.
- **Sin framework de UI** — los filtros y el carrusel son JavaScript plano. Nadie necesita saber
  React para tocar el contenido.
- **CSS plano** con variables (`src/styles/tokens.css`) — la misma paleta e identidad visual del
  documento de anteproyecto.

## Correr el sitio en local

```bash
npm install
npm run dev
```

Abre `http://localhost:4321`.

```bash
npm run build    # genera el sitio estático en dist/
npm run check    # valida tipos y el esquema de contenido
```

## Estructura

```
src/
  content/
    config.ts            Esquema de datos (proyectos, componentes, conceptos)
    proyectos/<categoria>/<slug>.md    Un archivo por proyecto
    componentes.yaml      Catálogo de precios — un solo lugar por componente
    conceptos.yaml         Glosario — la teoría se escribe una vez, se enlaza desde cada proyecto
  data/
    categorias.ts          Las 5 categorías + regla de qué entra en cada una
    advertencias.ts         Texto estándar de cada aviso de seguridad
    equipo.ts                Colaboradores (ver "Página de equipo" abajo)
  utils/
    dificultad.ts            Rúbrica de 6 ejes → nivel 1-5
    costos.ts                 Suma materiales contra el catálogo → banda de costo
  components/, layouts/, pages/
```

## Publicar un proyecto nuevo

1. Copia `PLANTILLA-PROYECTO.md` a `src/content/proyectos/<categoria>/<slug>.md`.
2. Llena los campos. Si un material o un concepto no existe todavía en
   `componentes.yaml` / `conceptos.yaml`, agrégalo ahí primero.
3. Súbelo como `estado: borrador` mientras lo armas y `revision` cuando esté listo para que
   alguien más lo revise. Solo pasa a `publicado` una vez montado y probado físicamente.
4. `npm run dev` valida el esquema en caliente.

### Publicar sin usar Git (editor visual)

El sitio incluye [Decap CMS](https://decapcms.org) en `/admin`, configurado para editar
proyectos con formularios en vez de archivos. Para probarlo en local, sin necesidad de configurar
nada de autenticación:

```bash
npx decap-server        # en una terminal aparte
npm run dev              # en otra
```

Abre `http://localhost:4321/admin` — los cambios se guardan directo en tu copia local del
repositorio (`local_backend: true` en `public/admin/config.yml`).

**Para producción** (que el editor funcione para cualquier colaborador, no solo en tu máquina)
hace falta una GitHub OAuth App — o desplegar en Netlify o Cloudflare Pages, que traen ese flujo
resuelto. Es un paso pendiente hasta que se elija el hosting definitivo; mientras tanto, publicar
por Git funciona igual de bien.

El catálogo de componentes y el glosario de conceptos (`componentes.yaml`, `conceptos.yaml`) no
están en el editor visual todavía — se editan directamente como archivo. Cambian poco y su
formato es más sensible a errores; no vale la pena la fricción de exponerlos aún.

## Decisiones ya tomadas

- Moneda de referencia: **COP**, sin conversión automática por ahora.
- Menú principal conserva las 5 categorías originales; el cruce entre categorías se resuelve con
  etiquetas (`etiquetas:`), no con una segunda jerarquía.
- Sin comentarios por ahora — cada guía enlaza a un formulario/issue para reportar errores.
- Dificultad siempre calculada por la rúbrica de 6 ejes, nunca escrita a mano.

## Pendiente

- Elegir plataforma de hosting (define cómo se resuelve el OAuth del editor visual).
- Reemplazar los dos proyectos de ejemplo por el primer proyecto piloto real, con fotos.
- Definir la plataforma de donación (el enlace en `/donaciones` es un marcador de posición).
- Completar `src/data/equipo.ts` con los colaboradores reales.
