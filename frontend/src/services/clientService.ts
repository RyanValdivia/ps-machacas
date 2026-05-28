import api from "../auth/services/api";
import type { Client } from "../types/client";

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ClientFilters {
  search?: string;
  cliTipoDoc?: string;
  edad_min?: number;
  edad_max?: number;
}

export interface BusquedaClienteResponse {
  encontrado: boolean;
  cliente?: Client;
  mensaje?: string;
}

export const getClients = async (
  search = "",
  page = 1,
  filters?: ClientFilters
): Promise<PaginatedResponse<Client>> => {
  const params = new URLSearchParams();
  
  if (search) {
    params.append('search', search);
  }
  params.append('page', page.toString());
  
  // Agregar filtros avanzados
  if (filters) {
    if (filters.cliTipoDoc) {
      params.append('cliTipoDoc', filters.cliTipoDoc);
    }
    if (filters.edad_min) {
      params.append('edad_min', filters.edad_min.toString());
    }
    if (filters.edad_max) {
      params.append('edad_max', filters.edad_max.toString());
    }
  }
  
  const res = await api.get(`/clients/client/?${params.toString()}`);
  return res.data;
};

export const createClient = async (
  data: Omit<Client, "cliCod">
): Promise<Client> => {
  const res = await api.post("/clients/client/", data);
  return res.data.data;
};

// Actualizar cliente
export const updateClient = async (
  clientId: number,
  data: Omit<Client, "cliCod">
): Promise<Client> => {
  const res = await api.put(`/clients/client/${clientId}/`, data);
  return res.data.data;
};

// Eliminar cliente
export const deleteClient = async (clientId: number): Promise<void> => {
  await api.delete(`/clients/client/${clientId}/`);
};

export const buscarClientePorDocumento = async (
  tipoDoc: string,
  numDoc: string
): Promise<BusquedaClienteResponse> => {
  try {
    const params = new URLSearchParams({
      tipo: tipoDoc,
      numero: numDoc
    });
    
    const response = await api.get(`/clients/buscar/?${params.toString()}`);
    
    // El backend devuelve { encontrado: boolean, cliente?: {...}, mensaje?: string }
    return response.data;
    
  } catch (error: any) {
    console.error('Error buscando cliente:', error);
    
    // Si es un error de red o del servidor
    if (error.response?.status === 404) {
      return {
        encontrado: false,
        mensaje: 'Cliente no encontrado'
      };
    }
    
    // Otros errores
    throw new Error(error.response?.data?.error || 'Error al buscar cliente');
  }
};