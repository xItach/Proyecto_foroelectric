import { defineCollection, z } from "astro:content";
import { file, glob } from "astro/loaders";

// Categoría principal: define la URL y el menú. Ver src/data/categorias.ts
// para el nombre visible y la regla de archivo de cada una.
const categoriaSlug = z.enum([
  "control",
  "alimentacion",
  "potencia",
  "audiovisuales",
  "entretenimiento",
]);

// Rúbrica de dificultad — 6 ejes, 0 a 2 puntos cada uno. El nivel 1–5 se
// calcula a partir de esto (src/utils/dificultad.ts), nunca se escribe a mano.
const ejeDificultad = z.union([z.literal(0), z.literal(1), z.literal(2)]);

const proyectos = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/proyectos" }),
  schema: z.object({
    titulo: z.string(),
    proposito: z.string().max(220),
    categoria: categoriaSlug,
    etiquetas: z.array(z.string()).default([]),

    dificultad: z.object({
      componentes: ejeDificultad,
      montaje: ejeDificultad,
      instrumentacion: ejeDificultad,
      programacion: ejeDificultad,
      riesgo_electrico: ejeDificultad,
      calibracion: ejeDificultad,
    }),

    tiempo: z.object({
      horas_min: z.number().positive(),
      horas_max: z.number().positive(),
      sesiones: z.number().int().positive(),
      perfil: z.string(),
    }),

    seguridad: z
      .object({
        red_electrica: z.boolean().default(false),
        advertencias: z.array(z.string()).default([]),
      })
      .default({ red_electrica: false, advertencias: [] }),

    // Enlaza al glosario (src/content/conceptos.yaml) + la aplicación
    // puntual en este circuito. La teoría general no se repite aquí.
    conceptos: z
      .array(
        z.object({
          slug: z.string(),
          nota: z.string(),
        }),
      )
      .default([]),

    materiales: z.array(
      z.object({
        ref: z.string(), // referencia al catálogo de componentes
        cantidad: z.number().int().positive().default(1),
        nota: z.string().optional(),
      }),
    ),

    herramientas: z.array(z.string()).default([]),

    apoyo: z
      .array(
        z.object({
          titulo: z.string(),
          url: z.string().url(),
          tipo: z.enum(["enlace", "pdf", "video", "datasheet"]).default("enlace"),
        }),
      )
      .default([]),

    imagenes: z
      .array(
        z.object({
          alt: z.string(),
          src: z.string().optional(), // vacío = placeholder, foto pendiente
        }),
      )
      .default([]),

    pasos: z
      .array(
        z.object({
          titulo: z.string(),
          contenido: z.string(),
          verificacion: z.string().optional(),
        }),
      )
      .default([]),

    diagramas: z
      .array(
        z.object({
          titulo: z.string(),
          alt: z.string(),
          src: z.string().optional(),
        }),
      )
      .default([]),

    resultados: z
      .array(
        z.object({
          parametro: z.string(),
          esperado: z.string(),
        }),
      )
      .default([]),

    fallas: z
      .array(
        z.object({
          sintoma: z.string(),
          causas: z.array(z.string()),
        }),
      )
      .default([]),

    notas_colaborador: z.string().optional(),

    estado: z.enum(["borrador", "revision", "publicado", "obsoleto"]).default("borrador"),
    probado_por: z.array(z.string()).default([]),
    actualizado: z.coerce.date(),
    licencia: z.string().default("CC-BY-SA-4.0"),
  }),
});

// Catálogo de componentes — objeto {referencia: datos}, un solo lugar para
// el precio de cada componente. Ver docs/anteproyecto.html §8.
const componentes = defineCollection({
  loader: file("./src/content/componentes.yaml"),
  schema: z.object({
    nombre: z.string(),
    precio: z.number().nonnegative(),
    moneda: z.literal("COP").default("COP"),
    verificado: z.coerce.date(),
    fuente: z.string().optional(),
    alternativas: z.array(z.string()).default([]),
  }),
});

// Glosario de conceptos — vocabulario controlado, una ficha reutilizable
// por concepto. Ver docs/anteproyecto.html §5.
const conceptos = defineCollection({
  loader: file("./src/content/conceptos.yaml"),
  schema: z.object({
    nombre: z.string(),
    resumen: z.string(),
  }),
});

export const collections = { proyectos, componentes, conceptos };
