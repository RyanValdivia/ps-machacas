import { Page, APIRequestContext, expect } from '@playwright/test';

export async function loginAs(page: Page, username: string, password: string) {
  await page.goto('/');
  await page.fill('#username', username);
  await page.fill('#password', password);
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/\/dashboard/);
}

/**
 * Resetea el stock de un producto vía API REST antes de que el test lo consuma.
 * Necesario porque los 3 proyectos de browser (chromium/firefox/webkit) comparten
 * la misma BD dentro de un mismo job de CI, y el seed solo corre una vez: sin este
 * reset, solo el primer browser que corre el test encuentra stock disponible.
 */
export async function resetProductStock(
  request: APIRequestContext,
  productCode: string,
  stock: number,
  username = 'gerente1',
  password = 'Admin123!'
) {
  const tokenRes = await request.post('/api/user/token/', {
    data: { usuNom: username, usuContra: password },
  });
  if (!tokenRes.ok()) {
    throw new Error(`No se pudo autenticar para resetear stock: ${tokenRes.status()}`);
  }
  const { access } = await tokenRes.json();

  const searchRes = await request.get(`/api/products/?search=${encodeURIComponent(productCode)}`, {
    headers: { Authorization: `Bearer ${access}` },
  });
  if (!searchRes.ok()) {
    throw new Error(`No se pudo buscar el producto ${productCode}: ${searchRes.status()}`);
  }
  const searchBody = await searchRes.json();
  const results = Array.isArray(searchBody) ? searchBody : searchBody.results;
  const product = results?.find((p: any) => p.prodCode === productCode) ?? results?.[0];
  if (!product) {
    throw new Error(`Producto ${productCode} no encontrado para resetear stock`);
  }

  const adjustRes = await request.post(`/api/products/${product.prodCod}/ajustar_stock/`, {
    headers: { Authorization: `Bearer ${access}` },
    data: { stock },
  });
  if (!adjustRes.ok()) {
    throw new Error(`No se pudo ajustar el stock de ${productCode}: ${adjustRes.status()}`);
  }
}
