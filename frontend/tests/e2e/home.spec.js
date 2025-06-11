import { test, expect } from "@playwright/test";

/**
 * Test to verify that the login page loads correctly
 */
test("should load the login page correctly", async ({ page }) => {
  // Navigate to the login page
  await page.goto("/login");

  // Verify that the login form elements are present
  await expect(page.locator('input[type="text"][required]')).toBeVisible();
  await expect(page.locator('input[type="password"][required]')).toBeVisible();
  await expect(page.locator('button[type="submit"]')).toBeVisible();

  // Verify the login button text
  await expect(page.locator('button[type="submit"]')).toContainText("Login");
});
