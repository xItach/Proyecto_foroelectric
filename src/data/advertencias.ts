// Advertencias como datos, no como prosa — docs/anteproyecto.html §12.
// El texto se genera siempre igual; el colaborador solo marca cuáles aplican.
export const ADVERTENCIAS: Record<string, string> = {
  "tension-de-red": "Este proyecto conecta directamente a tensión de red (120/240 V).",
  "capacitores-cargados": "Puede quedar energía almacenada en capacitores tras desconectar la alimentación.",
  "bateria-litio": "Usa baterías de litio: riesgo de incendio si se cortocircuitan, perforan o sobrecargan.",
  "superficie-caliente": "Alcanza temperaturas que pueden causar quemaduras al tacto.",
  "corriente-alta": "Maneja corrientes superiores a 1 A: riesgo de quemaduras o daño al equipo ante un corto.",
};

export function textoAdvertencia(slug: string): string {
  return ADVERTENCIAS[slug] ?? slug;
}
