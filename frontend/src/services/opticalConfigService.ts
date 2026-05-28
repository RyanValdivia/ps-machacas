import type { OpticalCenter } from "../types/opticalCenter";
import api from "../auth/services/api";

export const getOpticalCenter = async (): Promise<OpticalCenter> => {
    console.log('🔍 [DEBUG] getOpticalCenter: Iniciando petición GET /opticalcenter/');
    try {
        const res = await api.get("/opticalcenter/");
        console.log('✅ [DEBUG] getOpticalCenter: Respuesta exitosa:', res.data);
        return res.data;
    } catch (error: any) {
        console.error('❌ [DEBUG] getOpticalCenter: Error en petición:', error);
        console.error('❌ [DEBUG] Error details:', error.response?.data || error.message);
        throw error;
    }
}

export const updateOpticalCenter = async (data: OpticalCenter | FormData): Promise<OpticalCenter> => {
    console.log('🔍 [DEBUG] updateOpticalCenter: Iniciando actualización');
    console.log('📦 [DEBUG] Tipo de data:', data instanceof FormData ? 'FormData' : 'Object');
    
    if (data instanceof FormData) {
        console.log('📝 [DEBUG] Contenido del FormData:');
        for (let [key, value] of data.entries()) {
            if (value instanceof File) {
                console.log(`   - ${key}: File {name: "${value.name}", size: ${value.size} bytes, type: "${value.type}"}`);
            } else {
                console.log(`   - ${key}: ${value}`);
            }
        }
    } else {
        console.log('📝 [DEBUG] Contenido del objeto:', data);
    }
    
    try {
        const res = await api.put("/opticalcenter/1/", data, {
            headers: data instanceof FormData ? { 'Content-Type': 'multipart/form-data' } : {}
        });
        console.log('✅ [DEBUG] updateOpticalCenter: Actualización exitosa:', res.data);
        return res.data;
    } catch (error: any) {
        console.error('❌ [DEBUG] updateOpticalCenter: Error en actualización:', error);
        console.error('❌ [DEBUG] Error response:', error.response?.data);
        console.error('❌ [DEBUG] Error status:', error.response?.status);
        throw error;
    }
}

export const createOpticalCenter = async(data: OpticalCenter | FormData): Promise<OpticalCenter> => {
    console.log('🔍 [DEBUG] createOpticalCenter: Iniciando creación');
    console.log('📦 [DEBUG] Tipo de data:', data instanceof FormData ? 'FormData' : 'Object');
    
    if (data instanceof FormData) {
        console.log('📝 [DEBUG] Contenido del FormData:');
        for (let [key, value] of data.entries()) {
            if (value instanceof File) {
                console.log(`   - ${key}: File {name: "${value.name}", size: ${value.size} bytes, type: "${value.type}"}`);
            } else {
                console.log(`   - ${key}: ${value}`);
            }
        }
    } else {
        console.log('📝 [DEBUG] Contenido del objeto:', data);
    }
    
    try {
        const res = await api.post("/opticalcenter/", data, {
            headers: data instanceof FormData ? { 'Content-Type': 'multipart/form-data' } : {}
        });
        console.log('✅ [DEBUG] createOpticalCenter: Creación exitosa:', res.data);
        return res.data;
    } catch (error: any) {
        console.error('❌ [DEBUG] createOpticalCenter: Error en creación:', error);
        console.error('❌ [DEBUG] Error response:', error.response?.data);
        console.error('❌ [DEBUG] Error status:', error.response?.status);
        throw error;
    }
}