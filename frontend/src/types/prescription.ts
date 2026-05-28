export type Prescription = {
  recCod: number
  recFech: string
  recEstado: 'Activo' | 'Inactivo'
  recObservaciones?: string | null
  recInfoExtra?: string | null

  receDIP?: number | null
  receDIPCerca?: number | null
  receAdd?: number | null

  receEsfeOD?: number | null
  receCilinOD?: number | null
  receEjeOD?: number | null
  receAvccOD?: number | null

  receEsfeOI?: number | null
  receCilinOI?: number | null
  receEjeOI?: number | null
  receAvccOI?: number | null

  receEsExterna: boolean
  diagnostico: string[]

  cliCod: number
  optCod: number
}
