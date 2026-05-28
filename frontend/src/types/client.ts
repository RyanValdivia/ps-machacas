export type Client = {
  cliCod: number
  cliTipoDoc: 'DNI' | 'RUC' | 'CE'
  cliNumDoc: string
  cliNomCompleto: string
  cliTelef: string
  cliFechaNac?: string | null
  edad?: number | null
}