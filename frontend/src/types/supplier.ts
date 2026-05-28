
// Opciones de Departamento
export type DEPARTAMENTO_CHOICES =
  | 'AMAZONAS'
  | 'ANCASH'
  | 'APURIMAC'
  | 'AREQUIPA'
  | 'AYACUCHO'
  | 'CAJAMARCA'
  | 'CALLAO'
  | 'CUSCO'
  | 'HUANCAVELICA'
  | 'HUANUCO'
  | 'ICA'
  | 'JUNIN'
  | 'LA_LIBERTAD'
  | 'LAMBAYEQUE'
  | 'LIMA'
  | 'LORETO'
  | 'MADRE_DE_DIOS'
  | 'MOQUEGUA'
  | 'PASCO'
  | 'PIURA'
  | 'PUNO'
  | 'SAN_MARTIN'
  | 'TACNA'
  | 'TUMBES'
  | 'UCAYALI';

export interface Supplier {
  provCod?: number;
  provRuc?: string; // Opcional
  provRazSocial: string; // Obligatorio
  provDirec?: string; // Opcional
  provTele?: string; // Opcional
  provEmail?: string; // Opcional
  provCiu?: DEPARTAMENTO_CHOICES; // Opcional
  provEstado: 'Active' | 'Inactive';
}
