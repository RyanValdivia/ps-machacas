import { Page, expect } from '@playwright/test';

export async function loginAs(page: Page, username: string, password: string) {
  await page.goto('/');
  await page.fill('#username', username);
  await page.fill('#password', password);
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/\/dashboard/);
}
