import { test, expect } from "@playwright/test";

/**
 * Basic test to verify that the login page loads correctly
 */
test("should load the login page", async ({ page }) => {
  // Navigate to the login page
  await page.goto("/login");

  // Verify that the login form is displayed
  await expect(page.locator('input[type="text"][required]')).toBeVisible();
  await expect(page.locator('input[type="password"][required]')).toBeVisible();
  await expect(page.locator('button[type="submit"]')).toBeVisible();
});
