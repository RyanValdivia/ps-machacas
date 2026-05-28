//Choices
export type ESTADO_CAJA_CHOICES =
    |'ACTIVO'
    |'DESACTIVADO'
    |'SUSPENDIDO'

export interface Cash{
    cajCod : number;
    cajNom : string;
    usuCod : number;
    cajDes: string;
    cajEstado : ESTADO_CAJA_CHOICES;
}
export type ESTADO_CAJA_APERT_CHOICES =
    |'ABIERTA'
    |'CERRADA'
    |'ANULADA'
export interface CashOpening{
    cajAperCod : number;
    cajCod : number;
    usuCod : number;

    cajaApertuFechHora : Date;
    cajaAperMontInicial : number;

    cajaAperFechaHorCierre : Date    | null;
    cajaAperMontCierre : number | null;
    cajaAperMontEsperado : number | null;
    cajaAperDiferencia : number | null;
    cajaAperEstado : ESTADO_CAJA_APERT_CHOICES;
    cajaAperObservacio : string | null;
}