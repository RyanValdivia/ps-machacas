export interface OpticalCenter {
    optCod?: number;
    optNom: string;
    optLema?: string;
    optDir?: string;
    optProv?: string;
    optTel?: string;
    optLogo?: File | null;
    optLogoUrl?: string | null; // Nueva propiedad para la URL base64
}