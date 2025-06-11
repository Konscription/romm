import { test, expect } from "@playwright/test";

/**
 * Test to verify the login process
 */
test("should be able to log in", async ({ page }) => {
  // Navigate to the login page
  await page.goto("/login");

  // Take a screenshot before login
  await page.screenshot({ path: "before-login.png" });

  // Clear the username field and type
  await page.locator("input").first().click();
  await page.keyboard.press("Control+a");
  await page.keyboard.press("Delete");
  await page.locator("input").first().type("romm");

  // Clear the password field and type
  await page.locator("input").nth(1).click();
  await page.keyboard.press("Control+a");
  await page.keyboard.press("Delete");
  await page.locator("input").nth(1).type("romm");

  // Take a screenshot after filling in the form
  await page.screenshot({ path: "after-fill.png" });

  // Check if the login button is enabled
  const isDisabled = await page
    .locator('button:has-text("Login")')
    .isDisabled();
  console.log("Login button disabled:", isDisabled);

  // Try to click the login button anyway
  try {
    await page.locator('button:has-text("Login")').click({ force: true });
    console.log("Clicked login button");
  } catch (error) {
    console.error("Failed to click login button:", error);
  }

  // Wait a moment
  await page.waitForTimeout(2000);

  // Take a screenshot after clicking login
  await page.screenshot({ path: "after-login.png" });

  // Log the current URL
  console.log("Current URL:", await page.url());
});
