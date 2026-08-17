// Costos derivados del catálogo compartido — docs/anteproyecto.html §8.
// El proyecto nunca escribe un precio: referencia un componente y el costo
// se calcula desde src/content/componentes.yaml.

export interface MaterialRef {
  ref: string;
  cantidad: number;
  nota?: string;
}

export interface ComponenteCatalogo {
  nombre: string;
  precio: number;
  moneda: "COP";
  verificado: Date;
  fuente?: string;
  alternativas: string[];
}

export interface LineaCosto {
  ref: string;
  cantidad: number;
  nota?: string;
  componente?: ComponenteCatalogo;
  subtotal: number;
}

export interface ResumenCosto {
  lineas: LineaCosto[];
  faltantes: string[]; // refs sin entrada en el catálogo
  total: number;
  totalMin: number;
  totalMax: number;
  banda: "bajo" | "medio" | "alto";
  precioDesactualizado: boolean; // alguna línea con más de 6 meses sin verificar
}

// Margen de variabilidad mostrado como rango: el precio del catálogo es un
// punto de referencia, no una cotización — nunca se presenta como exacto.
const MARGEN_VARIABILIDAD = 0.15;

const UMBRAL_BAJO = 50_000;
const UMBRAL_MEDIO = 150_000;
const MESES_DESACTUALIZADO = 6;

export function calcularCosto(
  materiales: MaterialRef[],
  catalogo: Map<string, ComponenteCatalogo>,
): ResumenCosto {
  const hoy = new Date();
  const limiteDesactualizado = new Date(hoy);
  limiteDesactualizado.setMonth(limiteDesactualizado.getMonth() - MESES_DESACTUALIZADO);

  const faltantes: string[] = [];
  let precioDesactualizado = false;

  const lineas: LineaCosto[] = materiales.map((m) => {
    const componente = catalogo.get(m.ref);
    if (!componente) {
      faltantes.push(m.ref);
      return { ref: m.ref, cantidad: m.cantidad, nota: m.nota, subtotal: 0 };
    }
    if (componente.verificado < limiteDesactualizado) precioDesactualizado = true;
    return {
      ref: m.ref,
      cantidad: m.cantidad,
      nota: m.nota,
      componente,
      subtotal: componente.precio * m.cantidad,
    };
  });

  const total = lineas.reduce((acc, l) => acc + l.subtotal, 0);
  const totalMin = Math.round(total * (1 - MARGEN_VARIABILIDAD));
  const totalMax = Math.round(total * (1 + MARGEN_VARIABILIDAD));

  const banda: ResumenCosto["banda"] =
    total < UMBRAL_BAJO ? "bajo" : total < UMBRAL_MEDIO ? "medio" : "alto";

  return { lineas, faltantes, total, totalMin, totalMax, banda, precioDesactualizado };
}

export function formatoCOP(valor: number): string {
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(valor);
}

export const ETIQUETA_BANDA: Record<ResumenCosto["banda"], string> = {
  bajo: "Costo bajo",
  medio: "Costo medio",
  alto: "Costo alto",
};
