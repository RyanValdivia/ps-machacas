import api from "../auth/services/api";
import type { PaginatedResponse } from "../auth/services/product/productService";
import type { Prescription } from "../types/prescription";

/* =======================
   GET RECIPES
======================= */

// Listar recetas (puede filtrar por cliente y búsqueda)
export const getRecipes = async (
  page = 1,
  params?: {
    cliCod?: number;
    search?: string;
  }
): Promise<PaginatedResponse<Prescription>> => {

  const res = await api.get("/clients/prescription/", {
    params: { page, ...params },
  });

  return res.data; // 👈 NO .data.data
};


export const createRecipe = async (
  data: Omit<Prescription, "recCod">
): Promise<Prescription> => {
  const res = await api.post("/clients/prescription/", data);
  return res.data.data;
};



export const updateRecipe = async (
  recipeId: number,
  data: Omit<Prescription, "recCod">
): Promise<Prescription> => {
  const res = await api.put(`/clients/prescription/${recipeId}/`, data);
  return res.data.data;
};


export const deleteRecipe = async (recipeId: number): Promise<void> => {
  await api.delete(`/clients/prescription/${recipeId}/`);
};
