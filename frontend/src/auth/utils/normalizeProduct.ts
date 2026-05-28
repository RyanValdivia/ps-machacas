import type { Product } from "../types/product/product";

export const normalizeProduct = (p: Product): Product => ({
  ...p,
  // Campos que a veces pueden venir null/undefined o '' dependiendo de la data histórica
  prodMarca: (p.prodMarca ?? "").toString(),
  prodColor: (p.prodColor ?? "").toString(),
  prodTalla: (p.prodTalla ?? "").toString(),
  prodMate: (p.prodMate ?? "N").toString(),
  prodGenero: (p.prodGenero ?? "Unisex").toString(),
  prodEstado: (p.prodEstado ?? "Active").toString(),

  // Displays (si no vienen, dejamos string vacío para evitar N/A)
  material_display: (p.material_display ?? "").toString(),
  genero_display: (p.genero_display ?? "").toString(),
  estado_display: (p.estado_display ?? "").toString(),

  // Stock mínimo por defecto
  prodStockMin: Number((p as any).prodStockMin ?? 0),
  prodPrecioVenta: Number(p.prodPrecioVenta),
  prodCostoInv: Number(p.prodCostoInv),
  margen_ganancia: p.margen_ganancia !== null
    ? Number(p.margen_ganancia)
    : null,
});
