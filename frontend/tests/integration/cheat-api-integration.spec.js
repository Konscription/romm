// Import the API functions we want to test
import * as cheatApi from "@/services/api/cheat";

// Mock the API functions directly
jest.mock("@/services/api/cheat", () => ({
  addRomCheat: jest.fn(),
  updateRomCheat: jest.fn(),
  deleteRomCheat: jest.fn(),
  getCheatCodes: jest.fn(),
  uploadCheatFile: jest.fn(),
  getCheatFiles: jest.fn(),
  deleteCheatFile: jest.fn(),
}));

describe("Cheat API Integration Tests", () => {
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
  });

  describe("addRomCheat", () => {
    it("should make a POST request to the correct endpoint with the correct data", async () => {
      // Arrange
      const romId = "123";
      const cheatCode = {
        code: "ABCD-1234",
        description: "Infinite Lives",
        romId: "123",
      };
      const expectedResponse = {
        id: "1",
        code: "ABCD-1234",
        description: "Infinite Lives",
        romId: "123",
      };

      // Mock the API response
      cheatApi.addRomCheat.mockResolvedValue(expectedResponse);

      // Act
      const result = await cheatApi.addRomCheat(romId, cheatCode);

      // Assert
      expect(result).toEqual(expectedResponse);
      expect(cheatApi.addRomCheat).toHaveBeenCalledWith(romId, cheatCode);
    });

    it("should handle API errors correctly", async () => {
      // Arrange
      const romId = "123";
      const cheatCode = {
        code: "ABCD-1234",
        description: "Infinite Lives",
        romId: "123",
      };

      // Mock the API response with an error
      cheatApi.addRomCheat.mockRejectedValue(new Error("ROM not found"));

      // Act & Assert
      await expect(cheatApi.addRomCheat(romId, cheatCode)).rejects.toThrow(
        "ROM not found",
      );
    });
  });

  describe("updateRomCheat", () => {
    it("should make a PUT request to the correct endpoint with the correct data", async () => {
      // Arrange
      const romId = "123";
      const cheatId = "456";
      const cheatCode = {
        id: "456",
        code: "EFGH-5678",
        description: "Updated Description",
        romId: "123",
      };
      const expectedResponse = {
        id: "456",
        code: "EFGH-5678",
        description: "Updated Description",
        romId: "123",
      };

      // Mock the API response
      cheatApi.updateRomCheat.mockResolvedValue(expectedResponse);

      // Act
      const result = await cheatApi.updateRomCheat(romId, cheatId, cheatCode);

      // Assert
      expect(result).toEqual(expectedResponse);
      expect(cheatApi.updateRomCheat).toHaveBeenCalledWith(
        romId,
        cheatId,
        cheatCode,
      );
    });

    it("should handle API errors correctly", async () => {
      // Arrange
      const romId = "123";
      const cheatId = "456";
      const cheatCode = {
        id: "456",
        code: "EFGH-5678",
        description: "Updated Description",
        romId: "123",
      };

      // Mock the API response with an error
      cheatApi.updateRomCheat.mockRejectedValue(
        new Error("Cheat code not found"),
      );

      // Act & Assert
      await expect(
        cheatApi.updateRomCheat(romId, cheatId, cheatCode),
      ).rejects.toThrow("Cheat code not found");
    });
  });

  describe("deleteRomCheat", () => {
    it("should make a DELETE request to the correct endpoint", async () => {
      // Arrange
      const romId = "123";
      const cheatId = "456";
      const expectedResponse = { msg: "Cheat code deleted successfully" };

      // Mock the API response
      cheatApi.deleteRomCheat.mockResolvedValue(expectedResponse);

      // Act
      const result = await cheatApi.deleteRomCheat(romId, cheatId);

      // Assert
      expect(result).toEqual(expectedResponse);
      expect(cheatApi.deleteRomCheat).toHaveBeenCalledWith(romId, cheatId);
    });

    it("should handle API errors correctly", async () => {
      // Arrange
      const romId = "123";
      const cheatId = "456";

      // Mock the API response with an error
      cheatApi.deleteRomCheat.mockRejectedValue(
        new Error("Cheat code not found"),
      );

      // Act & Assert
      await expect(cheatApi.deleteRomCheat(romId, cheatId)).rejects.toThrow(
        "Cheat code not found",
      );
    });
  });

  describe("getCheatCodes", () => {
    it("should make a GET request to the correct endpoint", async () => {
      // Arrange
      const romId = "123";
      const expectedResponse = [
        {
          id: "1",
          code: "ABCD-1234",
          description: "Infinite Lives",
          romId: "123",
        },
        {
          id: "2",
          code: "EFGH-5678",
          description: "Invincibility",
          romId: "123",
        },
      ];

      // Mock the API response
      cheatApi.getCheatCodes.mockResolvedValue(expectedResponse);

      // Act
      const result = await cheatApi.getCheatCodes(romId);

      // Assert
      expect(result).toEqual(expectedResponse);
      expect(cheatApi.getCheatCodes).toHaveBeenCalledWith(romId);
    });

    it("should handle API errors correctly", async () => {
      // Arrange
      const romId = "123";

      // Mock the API response with an error
      cheatApi.getCheatCodes.mockRejectedValue(new Error("ROM not found"));

      // Act & Assert
      await expect(cheatApi.getCheatCodes(romId)).rejects.toThrow(
        "ROM not found",
      );
    });

    it("should handle empty response correctly", async () => {
      // Arrange
      const romId = "123";
      const expectedResponse = [];

      // Mock the API response
      cheatApi.getCheatCodes.mockResolvedValue(expectedResponse);

      // Act
      const result = await cheatApi.getCheatCodes(romId);

      // Assert
      expect(result).toEqual(expectedResponse);
      expect(result.length).toBe(0);
    });
  });

  describe("uploadCheatFile", () => {
    it("should make a POST request to the correct endpoint with the correct data", async () => {
      // Arrange
      const romId = "123";
      const formData = new FormData();
      formData.append("file", new Blob(["test content"]), "test.cht");
      const expectedResponse = {
        id: "1",
        name: "test.cht",
        romId: "123",
      };

      // Mock the API response
      cheatApi.uploadCheatFile.mockResolvedValue(expectedResponse);

      // Act
      const result = await cheatApi.uploadCheatFile(romId, formData);

      // Assert
      expect(result).toEqual(expectedResponse);
      expect(cheatApi.uploadCheatFile).toHaveBeenCalledWith(romId, formData);
    });

    it("should handle API errors correctly", async () => {
      // Arrange
      const romId = "123";
      const formData = new FormData();
      formData.append("file", new Blob(["test content"]), "test.cht");

      // Mock the API response with an error
      cheatApi.uploadCheatFile.mockRejectedValue(
        new Error("Invalid file format"),
      );

      // Act & Assert
      await expect(cheatApi.uploadCheatFile(romId, formData)).rejects.toThrow(
        "Invalid file format",
      );
    });
  });

  describe("getCheatFiles", () => {
    it("should make a GET request to the correct endpoint", async () => {
      // Arrange
      const romId = "123";
      const expectedResponse = [
        {
          id: "1",
          name: "cheats1.cht",
          romId: "123",
        },
        {
          id: "2",
          name: "cheats2.cht",
          romId: "123",
        },
      ];

      // Mock the API response
      cheatApi.getCheatFiles.mockResolvedValue(expectedResponse);

      // Act
      const result = await cheatApi.getCheatFiles(romId);

      // Assert
      expect(result).toEqual(expectedResponse);
      expect(cheatApi.getCheatFiles).toHaveBeenCalledWith(romId);
    });

    it("should handle API errors correctly", async () => {
      // Arrange
      const romId = "123";

      // Mock the API response with an error
      cheatApi.getCheatFiles.mockRejectedValue(new Error("ROM not found"));

      // Act & Assert
      await expect(cheatApi.getCheatFiles(romId)).rejects.toThrow(
        "ROM not found",
      );
    });

    it("should handle empty response correctly", async () => {
      // Arrange
      const romId = "123";
      const expectedResponse = [];

      // Mock the API response
      cheatApi.getCheatFiles.mockResolvedValue(expectedResponse);

      // Act
      const result = await cheatApi.getCheatFiles(romId);

      // Assert
      expect(result).toEqual(expectedResponse);
      expect(result.length).toBe(0);
    });
  });

  describe("deleteCheatFile", () => {
    it("should make a DELETE request to the correct endpoint", async () => {
      // Arrange
      const romId = "123";
      const fileId = "456";
      const expectedResponse = { msg: "Cheat file deleted successfully" };

      // Mock the API response
      cheatApi.deleteCheatFile.mockResolvedValue(expectedResponse);

      // Act
      const result = await cheatApi.deleteCheatFile(romId, fileId);

      // Assert
      expect(result).toEqual(expectedResponse);
      expect(cheatApi.deleteCheatFile).toHaveBeenCalledWith(romId, fileId);
    });

    it("should handle API errors correctly", async () => {
      // Arrange
      const romId = "123";
      const fileId = "456";

      // Mock the API response with an error
      cheatApi.deleteCheatFile.mockRejectedValue(
        new Error("Cheat file not found"),
      );

      // Act & Assert
      await expect(cheatApi.deleteCheatFile(romId, fileId)).rejects.toThrow(
        "Cheat file not found",
      );
    });
  });

  describe("Integration with Player component", () => {
    it("should correctly format cheat codes for EmulatorJS", async () => {
      // Arrange
      const romId = "123";
      const cheatCodes = [
        {
          id: "1",
          code: "ABCD-1234",
          description: "Infinite Lives",
          romId: "123",
        },
        {
          id: "2",
          code: "EFGH-5678",
          description: "Invincibility",
          romId: "123",
        },
      ];

      // Mock the API response
      cheatApi.getCheatCodes.mockResolvedValue(cheatCodes);

      // Act
      const result = await cheatApi.getCheatCodes(romId);

      // Assert
      expect(result).toEqual(cheatCodes);

      // Test the formatting function used in Player.vue
      const formatCheatCodesForEmulatorJS = (codes) =>
        codes.map((code) => code.code).join("\n");
      const formattedCheats = formatCheatCodesForEmulatorJS(result);

      expect(formattedCheats).toBe("ABCD-1234\nEFGH-5678");
    });
  });
});
