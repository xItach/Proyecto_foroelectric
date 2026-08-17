export interface Colaborador {
  nombre: string;
  rol: string;
  bio: string;
  enlace?: string;
}

// Reemplaza esta entrada de ejemplo por los colaboradores reales del
// proyecto. Cada uno: nombre, rol dentro del equipo, y una bio corta.
export const equipo: Colaborador[] = [
  {
    nombre: "Nombre del colaborador",
    rol: "Fundador · Contenido y desarrollo",
    bio: "Reemplaza este texto con una bio corta: de dónde viene tu interés por la electrónica y qué parte del sitio llevas.",
  },
];
