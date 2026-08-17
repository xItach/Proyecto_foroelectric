// Rúbrica de dificultad — docs/anteproyecto.html §4.
// Seis ejes de 0 a 2 puntos. La suma cae en un nivel 1–5. El colaborador
// puntúa los ejes; el nivel y la etiqueta se calculan, nunca se opinan.

export interface EjesDificultad {
  componentes: 0 | 1 | 2;
  montaje: 0 | 1 | 2;
  instrumentacion: 0 | 1 | 2;
  programacion: 0 | 1 | 2;
  riesgo_electrico: 0 | 1 | 2;
  calibracion: 0 | 1 | 2;
}

export interface NivelDificultad {
  puntos: number;
  nivel: 1 | 2 | 3 | 4 | 5;
  etiqueta: string;
}

const ETIQUETAS: Record<NivelDificultad["nivel"], string> = {
  1: "Introductorio",
  2: "Básico",
  3: "Intermedio",
  4: "Avanzado",
  5: "Experto",
};

export const EJE_LABELS: Record<keyof EjesDificultad, string> = {
  componentes: "Componentes",
  montaje: "Montaje",
  instrumentacion: "Instrumentación",
  programacion: "Programación",
  riesgo_electrico: "Riesgo eléctrico",
  calibracion: "Ajuste y calibración",
};

export function calcularDificultad(ejes: EjesDificultad): NivelDificultad {
  const puntos =
    ejes.componentes +
    ejes.montaje +
    ejes.instrumentacion +
    ejes.programacion +
    ejes.riesgo_electrico +
    ejes.calibracion;

  let nivel: NivelDificultad["nivel"];
  if (puntos <= 2) nivel = 1;
  else if (puntos <= 4) nivel = 2;
  else if (puntos <= 7) nivel = 3;
  else if (puntos <= 9) nivel = 4;
  else nivel = 5;

  return { puntos, nivel, etiqueta: ETIQUETAS[nivel] };
}
