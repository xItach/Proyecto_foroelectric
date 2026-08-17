export interface Categoria {
  slug: string;
  nombre: string;
  descripcion: string;
  // Regla de archivo: qué entra y qué no, para que el criterio no dependa
  // de quién publique. Ver docs/anteproyecto.html §9.
  regla: string;
}

export const categorias: Categoria[] = [
  {
    slug: "control",
    nombre: "Control",
    descripcion: "Circuitos que toman una decisión o gobiernan otro circuito.",
    regla:
      "Entra si la función principal es decidir, temporizar o regular un comportamiento (lógica, temporizadores, microcontroladores). No entra si el control es incidental a un circuito de potencia o alimentación.",
  },
  {
    slug: "alimentacion",
    nombre: "Alimentación",
    descripcion: "Fuentes, reguladores y todo lo que entrega energía a otro circuito.",
    regla:
      "Entra si el circuito existe para producir o regular una tensión o corriente de salida. No entra si la fuente es solo un paso incidental dentro de un proyecto clasificado en otra categoría.",
  },
  {
    slug: "potencia",
    nombre: "Potencia",
    descripcion: "Circuitos que conmutan o entregan energía significativa a una carga.",
    regla:
      "Entra si el circuito conmuta, amplifica o entrega potencia relevante (motores, calefacción, amplificadores de audio en su etapa de salida). No entra si la carga es solo indicadora (un LED).",
  },
  {
    slug: "audiovisuales",
    nombre: "Audiovisuales",
    descripcion: "Circuitos de audio, video o imagen: su función es procesar o reproducir señal.",
    regla:
      "Entra si el circuito procesa, amplifica o genera señal de audio o video. No entra si el audio o video es solo el resultado de un proyecto clasificado por su función en otra categoría — ahí va como etiqueta.",
  },
  {
    slug: "entretenimiento",
    nombre: "Entretenimiento",
    descripcion: "Juegos, efectos y proyectos pensados para jugar o exhibir.",
    regla:
      "Entra si el propósito declarado del proyecto es lúdico o de exhibición, no una herramienta de banco. Ante la duda con Audiovisuales, gana la categoría que describa el propósito y la otra queda como etiqueta.",
  },
];

export function categoriaPorSlug(slug: string): Categoria | undefined {
  return categorias.find((c) => c.slug === slug);
}
