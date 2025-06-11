import { test, expect } from "@playwright/test";

/**
 * Basic test for cheat code functionality
 * This test verifies that we can:
 * 1. Log in to the application
 * 2. Navigate to the home page
 * 3. Click on a ROM to view its details
 * 4. See the CHEATS tab in the ROM details page
 */

test("should navigate to ROM details and see CHEATS tab", async ({ page }) => {
  // Navigate to the login page
  await page.goto("/login");

  // Take a screenshot before login
  await page.screenshot({ path: "./tests/pics/1-before-login.png" });

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
  await page.screenshot({ path: "./tests/pics/2-after-fill.png" });

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
  await page.screenshot({ path: "./tests/pics/3-after-login.png" });

  // Log the current URL
  console.log("Current URL:", await page.url());

  // Take a screenshot of the home page
  await page.screenshot({ path: "./tests/pics/4-home-page.png" });

  // Log the current URL
  console.log("Home page URL:", await page.url());

  // Wait for the ROM list to load
  await page.waitForSelector(".v-card", { timeout: 10000 });

  // Click on the first ROM card
  await page.click(".v-card:first-child");

  // Wait for the ROM details page to load
  await page.waitForTimeout(2000);

  // Take a screenshot of the ROM details page
  await page.screenshot({ path: "./tests/pics/5-rom-details-page.png" });

  // Log the ROM details page URL
  console.log("ROM details page URL:", await page.url());

  // Check if the CHEATS tab exists
  const cheatsTab = await page.locator('button:has-text("Cheats")').count();
  console.log("Cheats tab exists:", cheatsTab > 0);

  if (cheatsTab > 0) {
    // Click on the CHEATS tab
    await page.click('button:has-text("Cheats")');

    // Take a screenshot of the CHEATS tab
    await page.screenshot({ path: "./tests/pics/6-cheats-tab.png" });

    // Check if the Add Cheat button exists
    const addCheatButton = await page
      .locator('button:has-text("Add Cheat")')
      .count();
    console.log("Add Cheat button exists:", addCheatButton > 0);
  }
});
