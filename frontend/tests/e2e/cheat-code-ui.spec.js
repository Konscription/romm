import { test, expect } from "@playwright/test";

/**
 * User Acceptance Tests for Cheat Code UI and Functionality
 *
 * These tests verify that users can:
 * 1. Add, edit, and delete cheat codes through the UI
 * 2. Upload, download, and delete cheat files through the UI
 * 3. See cheat codes correctly applied when playing a ROM
 * 4. See appropriate error messages when operations fail
 * 5. Use the UI correctly with different ROMs and emulators
 */

// Test data
const testRom = {
  id: 1, // PaRappa the Rapper
  name: "PaRappa the Rapper.zip",
  platform_slug: "psx",
};

const testCheatCode = {
  name: "Infinite Lives",
  code: "SXYIZVSE",
  description: "Never lose a life when hit",
  type: "GAME_GENIE",
};

const updatedCheatCode = {
  name: "Infinite Lives (Updated)",
  code: "SXYIZVSE",
  description: "Updated description for infinite lives",
  type: "GAME_GENIE",
};

test.describe("Cheat Code UI Tests", () => {
  test.beforeEach(async ({ page }) => {
    // Login and navigate to the ROM details page
    await page.goto("/login");

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

    // Try to click the login button
    try {
      await page.locator('button:has-text("Login")').click({ force: true });
    } catch (error) {
      console.error("Failed to click login button:", error);
    }

    // Wait a moment
    await page.waitForTimeout(2000);

    // Navigate to the ROM details page
    await page.goto(`/rom/${testRom.id}`);

    // Wait for the page to load
    await page.waitForTimeout(2000);
  });

  test("should display the cheat codes tab in ROM details", async ({
    page,
  }) => {
    // Click on the Cheats tab
    await page.click('button:has-text("Cheats")');

    // Verify the cheat codes section is displayed
    await expect(page.locator('span.text-h6:has-text("Cheats")')).toBeVisible();
    await expect(page.locator('button:has-text("Add Cheat")')).toBeVisible();
  });

  test("should add a new cheat code", async ({ page }) => {
    // Click on the Cheats tab
    await page.click('button:has-text("Cheats")');

    // Click the Add Cheat button
    await page.click('button:has-text("Add Cheat")');

    // Fill in the cheat code form
    await page.fill(
      'input[type="text"][required]:nth-of-type(1)',
      testCheatCode.name,
    );
    await page.fill(
      'input[type="text"][required]:nth-of-type(2)',
      testCheatCode.code,
    );
    await page.fill("textarea", testCheatCode.description);
    await page.selectOption("select", testCheatCode.type);

    // Submit the form
    await page.click('button:has-text("Add Cheat")');

    // Verify the cheat code was added
    await expect(
      page.locator(`tr:has-text("${testCheatCode.name}")`),
    ).toBeVisible();
    await expect(
      page.locator(`tr:has-text("${testCheatCode.code}")`),
    ).toBeVisible();
  });

  test("should edit an existing cheat code", async ({ page }) => {
    // Click on the Cheats tab
    await page.click('button:has-text("Cheats")');

    // Find and click the edit button for the cheat code
    await page.click(`tr:has-text("${testCheatCode.name}") button.edit-button`);

    // Update the cheat code form
    await page.fill(
      'input[type="text"][required]:nth-of-type(1)',
      updatedCheatCode.name,
    );
    await page.fill("textarea", updatedCheatCode.description);

    // Submit the form
    await page.click('button:has-text("Save")');

    // Verify the cheat code was updated
    await expect(
      page.locator(`tr:has-text("${updatedCheatCode.name}")`),
    ).toBeVisible();
    await expect(
      page.locator(`tr:has-text("${updatedCheatCode.description}")`),
    ).toBeVisible();
  });

  test("should delete a cheat code", async ({ page }) => {
    // Click on the Cheats tab
    await page.click('button:has-text("Cheats")');

    // Find and click the delete button for the cheat code
    await page.click(
      `tr:has-text("${updatedCheatCode.name}") button.delete-button`,
    );

    // Confirm deletion in the dialog
    await page.click('button:has-text("Confirm")');

    // Verify the cheat code was deleted
    await expect(
      page.locator(`tr:has-text("${updatedCheatCode.name}")`),
    ).not.toBeVisible();
  });

  test("should upload a cheat file", async ({ page }) => {
    // Click on the Cheats tab
    await page.click('button:has-text("Cheats")');

    // Click the Add Cheat button
    await page.click('button:has-text("Add Cheat")');

    // Upload a cheat file
    const fileChooserPromise = page.waitForEvent("filechooser");
    await page.click('input[type="file"]');
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles({
      name: "test_cheats.cht",
      mimeType: "application/octet-stream",
      buffer: Buffer.from("Test cheat file content"),
    });

    // Submit the form
    await page.click('button:has-text("Upload")');

    // Verify the cheat file was uploaded
    await expect(page.locator('tr:has-text("test_cheats.cht")')).toBeVisible();
  });

  test("should download a cheat file", async ({ page }) => {
    // Click on the Cheats tab
    await page.click('button:has-text("Cheats")');

    // Setup download listener
    const downloadPromise = page.waitForEvent("download");

    // Click the download button for the cheat file
    await page.click('tr:has-text("test_cheats.cht") button.download-button');

    // Wait for the download to start
    const download = await downloadPromise;

    // Verify the download
    expect(download.suggestedFilename()).toBe("test_cheats.cht");
  });

  test("should delete a cheat file", async ({ page }) => {
    // Click on the Cheats tab
    await page.click('button:has-text("Cheats")');

    // Find and click the delete button for the cheat file
    await page.click('tr:has-text("test_cheats.cht") button.delete-button');

    // Confirm deletion in the dialog
    await page.click('button:has-text("Confirm")');

    // Verify the cheat file was deleted
    await expect(
      page.locator('tr:has-text("test_cheats.cht")'),
    ).not.toBeVisible();
  });

  test("should show error message when API request fails", async ({ page }) => {
    // Intercept API requests to simulate failure
    await page.route("**/api/rom/*/cheats", (route) => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({ detail: "Server error" }),
      });
    });

    // Click on the Cheats tab
    await page.click('button:has-text("Cheats")');

    // Click the Add Cheat button
    await page.click('button:has-text("Add Cheat")');

    // Fill in the cheat code form
    await page.fill(
      'input[type="text"][required]:nth-of-type(1)',
      testCheatCode.name,
    );
    await page.fill(
      'input[type="text"][required]:nth-of-type(2)',
      testCheatCode.code,
    );
    await page.fill("textarea", testCheatCode.description);
    await page.selectOption("select", testCheatCode.type);

    // Submit the form
    await page.click('button:has-text("Save")');

    // Verify error message is displayed
    await expect(
      page.locator('div:has-text("Failed to add cheat code")'),
    ).toBeVisible();
  });
});

test.describe("Cheat Code Functionality in Emulator", () => {
  test.beforeEach(async ({ page }) => {
    // Login and navigate to the ROM details page
    await page.goto("/login");

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

    // Try to click the login button
    try {
      await page.locator('button:has-text("Login")').click({ force: true });
    } catch (error) {
      console.error("Failed to click login button:", error);
    }

    // Wait a moment
    await page.waitForTimeout(2000);

    // Navigate to the ROM details page
    await page.goto(`/rom/${testRom.id}`);

    // Wait for the page to load
    await page.waitForTimeout(2000);
  });

  test("should apply cheat codes when playing a ROM", async ({ page }) => {
    // Add a test cheat code first
    await page.click('button:has-text("Cheats")');
    await page.click('button:has-text("Add Cheat")');
    await page.fill(
      'input[type="text"][required]:nth-of-type(1)',
      testCheatCode.name,
    );
    await page.fill(
      'input[type="text"][required]:nth-of-type(2)',
      testCheatCode.code,
    );
    await page.fill("textarea", testCheatCode.description);
    await page.selectOption("select", testCheatCode.type);
    await page.click('button:has-text("Save")');

    // Click the Play button
    await page.click('button:has-text("Play")');

    // Wait for the emulator to load
    await page.waitForSelector("#game");

    // Verify the EJS_cheats global variable is set correctly
    const cheatsSet = await page.evaluate(() => {
      return window.EJS_cheats === "SXYIZVSE";
    });

    expect(cheatsSet).toBe(true);

    // Verify the cheat menu is accessible in the emulator
    await page.click(".ejs_menu_button"); // Open the emulator menu
    await expect(page.locator('button:has-text("Cheats")')).toBeVisible();
  });

  test("should work with different ROM platforms", async ({ page }) => {
    // Test with a different ROM (Super Mario 64)
    const otherRom = {
      id: 2,
      name: "Super Mario 64",
      platform_slug: "n64",
    };

    // Navigate to the other ROM details page
    await page.goto(`/rom/${otherRom.id}`);

    // Add a test cheat code
    await page.click('button:has-text("Cheats")');
    await page.click('button:has-text("Add Cheat")');

    // Fill in the cheat code form with N64-specific code
    await page.fill('input[type="text"][required]', "Infinite Lives");
    await page.fill(
      'input[type="text"][required]:nth-child(2)',
      "81249B34 00FF",
    );
    await page.fill("textarea", "Never lose a life");
    await page.selectOption("select", "GAME_SHARK");

    // Submit the form
    await page.click('button:has-text("Save")');

    // Click the Play button
    await page.click('button:has-text("Play")');

    // Wait for the emulator to load
    await page.waitForSelector("#game");

    // Verify the EJS_cheats global variable is set correctly
    const cheatsSet = await page.evaluate(() => {
      return window.EJS_cheats === "81249B34 00FF";
    });

    expect(cheatsSet).toBe(true);
  });

  test("should handle multiple cheat codes correctly", async ({ page }) => {
    // Navigate to the ROM details page
    await page.goto(`/rom/${testRom.id}`);

    // Click on the Cheats tab
    await page.click('button:has-text("Cheats")');

    // Add first cheat code
    await page.click('button:has-text("Add Cheat")');
    await page.fill(
      'input[type="text"][required]:nth-of-type(1)',
      "Infinite Lives",
    );
    await page.fill('input[type="text"][required]:nth-of-type(2)', "SXYIZVSE");
    await page.fill("textarea", "Never lose a life");
    await page.selectOption("select", "GAME_GENIE");
    await page.click('button:has-text("Save")');

    // Add second cheat code
    await page.click('button:has-text("Add Cheat")');
    await page.fill(
      'input[type="text"][required]:nth-of-type(1)',
      "Invincibility",
    );
    await page.fill('input[type="text"][required]:nth-of-type(2)', "AEKZZZIA");
    await page.fill("textarea", "Cannot be hurt by enemies");
    await page.selectOption("select", "GAME_GENIE");
    await page.click('button:has-text("Save")');

    // Click the Play button
    await page.click('button:has-text("Play")');

    // Wait for the emulator to load
    await page.waitForSelector("#game");

    // Verify the EJS_cheats global variable is set correctly with both codes
    const cheatsSet = await page.evaluate(() => {
      return window.EJS_cheats === "SXYIZVSE\nAEKZZZIA";
    });

    expect(cheatsSet).toBe(true);
  });
});

test.describe("Cheat Code UI Responsiveness", () => {
  test("should display correctly on mobile devices", async ({ page }) => {
    // Set viewport to mobile size
    await page.setViewportSize({ width: 375, height: 667 });

    // Login and navigate to the ROM details page
    await page.goto("/login");

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

    // Try to click the login button
    try {
      await page.locator('button:has-text("Login")').click({ force: true });
    } catch (error) {
      console.error("Failed to click login button:", error);
    }

    // Wait a moment
    await page.waitForTimeout(2000);

    // Navigate to the ROM details page
    await page.goto(`/rom/${testRom.id}`);

    // Wait for the page to load
    await page.waitForTimeout(2000);

    // Click on the Cheats tab
    await page.click('button:has-text("Cheats")');

    // Verify the responsive layout
    await expect(page.locator(".cheat-codes-section")).toBeVisible();
    await expect(page.locator('button:has-text("Add Cheat")')).toBeVisible();

    // Verify table is responsive
    const tableWidth = await page
      .locator("table.cheat-codes-table")
      .evaluate((el) => el.offsetWidth);
    expect(tableWidth).toBeLessThanOrEqual(375);
  });
});
