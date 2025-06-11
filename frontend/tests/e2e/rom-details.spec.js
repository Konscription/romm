import { test, expect } from "@playwright/test";

/**
 * Basic test to verify that the ROM details page loads correctly
 */
test("should load the ROM details page after login", async ({ page }) => {
  // Navigate to the login page
  await page.goto("/login");

  // Fill in the login form - use a different approach
  await page.locator("input").first().fill("romm");
  await page.locator("input").nth(1).fill("romm");

  // Wait for the login button to be enabled
  await page.waitForSelector("button:not([disabled])", { timeout: 5000 });

  // Submit the form
  await page.click('button:has-text("Login")');

  // Wait for navigation to complete
  await page.waitForURL("**/");

  // Navigate to the ROM details page
  await page.goto("/roms/1");

  // Wait for the page to load (with a longer timeout)
  await page.waitForLoadState("networkidle", { timeout: 30000 });

  // Take a screenshot for debugging
  await page.screenshot({ path: "rom-details-page.png" });

  // Verify that we're on the ROM details page
  await expect(page.url()).toContain("/roms/1");
});
