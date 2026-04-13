import { expect, test } from '@playwright/test'

test('loads the frontend scaffold', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: /get started/i })).toBeVisible()
})
