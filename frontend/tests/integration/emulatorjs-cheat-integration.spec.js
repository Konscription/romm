import { mount, flushPromises } from "@vue/test-utils";
import Player from "@/views/Player/EmulatorJS/Player.vue";
import { createTestingPinia } from "@pinia/testing";
import storeRoms from "@/stores/roms";
import storePlaying from "@/stores/playing";
import * as cheatApi from "@/services/api/cheat";

// Mock the cheat API
jest.mock("@/services/api/cheat", () => ({
  getCheatCodes: jest.fn(),
}));

// Mock the EmulatorJS global variables and functions
global.EJS_emulator = {
  callEvent: jest.fn(),
  displayMessage: jest.fn(),
  pause: jest.fn(),
  toggleFullscreen: jest.fn(),
  storage: {
    states: {
      put: jest.fn(),
      get: jest.fn().mockResolvedValue(new Uint8Array()),
    },
  },
  settings: {},
  getBaseFileName: jest.fn().mockReturnValue("test-rom"),
  saveInBrowserSupported: jest.fn().mockReturnValue(true),
  gameManager: {
    loadState: jest.fn(),
    getState: jest.fn().mockReturnValue(new Uint8Array()),
    getSaveFile: jest.fn().mockReturnValue(new Uint8Array()),
    screenshot: jest.fn().mockResolvedValue(new Uint8Array()),
  },
};

// Mock window functions
Object.defineProperty(window, "scrollTo", { value: jest.fn() });
Object.defineProperty(window, "history", {
  value: {
    back: jest.fn(),
  },
});

// Mock document.querySelector
document.querySelector = jest.fn().mockReturnValue({
  classList: {
    add: jest.fn(),
    remove: jest.fn(),
  },
});

describe("EmulatorJS Cheat Code Integration Tests", () => {
  let wrapper;
  let pinia;

  // Sample ROM data for testing
  const mockRom = {
    id: 123,
    platform_slug: "nes",
    fs_name_no_tags: "Super Mario Bros",
    files: [{ id: 1, name: "Super Mario Bros.nes" }],
  };

  // Sample cheat codes for testing
  const mockCheatCodes = [
    {
      id: "1",
      code: "SXYIZVSE",
      description: "Infinite Lives",
      romId: "123",
    },
    {
      id: "2",
      code: "AEKZZZIA",
      description: "Invincibility",
      romId: "123",
    },
  ];

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();

    // Create a fresh Pinia store before each test
    pinia = createTestingPinia();

    // Set up the ROM store with our mock ROM
    const romsStore = storeRoms(pinia);
    romsStore.update = jest.fn();

    // Set up the playing store
    const playingStore = storePlaying(pinia);
    playingStore.playing = false;
    playingStore.fullScreen = false;
  });

  afterEach(() => {
    // Clean up after each test
    if (wrapper) {
      wrapper.unmount();
    }
  });

  describe("Cheat Code Fetching", () => {
    it("should fetch cheat codes when the component is mounted", async () => {
      // Arrange
      cheatApi.getCheatCodes.mockResolvedValue(mockCheatCodes);

      // Act
      wrapper = mount(Player, {
        props: {
          rom: mockRom,
          save: null,
          state: null,
          bios: null,
          core: "nes",
          disc: null,
        },
        global: {
          plugins: [pinia],
          stubs: {
            // Stub any components or directives as needed
          },
          provide: {
            emitter: {
              on: jest.fn(),
              off: jest.fn(),
              emit: jest.fn(),
            },
          },
        },
      });

      // Wait for promises to resolve
      await flushPromises();

      // Assert
      expect(cheatApi.getCheatCodes).toHaveBeenCalledWith("123");
      expect(window.EJS_cheats).toBeDefined();
      expect(window.EJS_cheats).toBe("SXYIZVSE\nAEKZZZIA");
    });

    it("should handle empty cheat codes response", async () => {
      // Arrange
      cheatApi.getCheatCodes.mockResolvedValue([]);

      // Act
      wrapper = mount(Player, {
        props: {
          rom: mockRom,
          save: null,
          state: null,
          bios: null,
          core: "nes",
          disc: null,
        },
        global: {
          plugins: [pinia],
          stubs: {
            // Stub any components or directives as needed
          },
          provide: {
            emitter: {
              on: jest.fn(),
              off: jest.fn(),
              emit: jest.fn(),
            },
          },
        },
      });

      // Wait for promises to resolve
      await flushPromises();

      // Assert
      expect(cheatApi.getCheatCodes).toHaveBeenCalledWith("123");
      expect(window.EJS_cheats).toBeUndefined();
    });

    it("should handle API errors when fetching cheat codes", async () => {
      // Arrange
      cheatApi.getCheatCodes.mockRejectedValue(new Error("Server error"));

      // Spy on console.error
      const consoleErrorSpy = jest.spyOn(console, "error").mockImplementation();

      // Act
      wrapper = mount(Player, {
        props: {
          rom: mockRom,
          save: null,
          state: null,
          bios: null,
          core: "nes",
          disc: null,
        },
        global: {
          plugins: [pinia],
          stubs: {
            // Stub any components or directives as needed
          },
          provide: {
            emitter: {
              on: jest.fn(),
              off: jest.fn(),
              emit: jest.fn(),
            },
          },
        },
      });

      // Wait for promises to resolve
      await flushPromises();

      // Assert
      expect(cheatApi.getCheatCodes).toHaveBeenCalledWith("123");
      expect(consoleErrorSpy).toHaveBeenCalled();
      expect(window.EJS_cheats).toBeUndefined();

      // Clean up
      consoleErrorSpy.mockRestore();
    });
  });

  describe("Cheat Code Formatting", () => {
    it("should correctly format cheat codes for EmulatorJS", async () => {
      // Arrange
      const formatCheatCodesForEmulatorJS = (cheatCodes) => {
        return cheatCodes.map((code) => code.code).join("\n");
      };

      // Act
      const formattedCheats = formatCheatCodesForEmulatorJS(mockCheatCodes);

      // Assert
      expect(formattedCheats).toBe("SXYIZVSE\nAEKZZZIA");
    });

    it("should handle a single cheat code correctly", async () => {
      // Arrange
      const singleCheatCode = [mockCheatCodes[0]];
      cheatApi.getCheatCodes.mockResolvedValue(singleCheatCode);

      // Act
      wrapper = mount(Player, {
        props: {
          rom: mockRom,
          save: null,
          state: null,
          bios: null,
          core: "nes",
          disc: null,
        },
        global: {
          plugins: [pinia],
          stubs: {
            // Stub any components or directives as needed
          },
          provide: {
            emitter: {
              on: jest.fn(),
              off: jest.fn(),
              emit: jest.fn(),
            },
          },
        },
      });

      // Wait for promises to resolve
      await flushPromises();

      // Assert
      expect(window.EJS_cheats).toBe("SXYIZVSE");
    });
  });

  describe("EJS_cheats Global Variable", () => {
    it("should set the EJS_cheats global variable when cheat codes are available", async () => {
      // Arrange
      cheatApi.getCheatCodes.mockResolvedValue(mockCheatCodes);

      // Act
      wrapper = mount(Player, {
        props: {
          rom: mockRom,
          save: null,
          state: null,
          bios: null,
          core: "nes",
          disc: null,
        },
        global: {
          plugins: [pinia],
          stubs: {
            // Stub any components or directives as needed
          },
          provide: {
            emitter: {
              on: jest.fn(),
              off: jest.fn(),
              emit: jest.fn(),
            },
          },
        },
      });

      // Wait for promises to resolve
      await flushPromises();

      // Assert
      expect(window.EJS_cheats).toBeDefined();
      expect(window.EJS_cheats).toBe("SXYIZVSE\nAEKZZZIA");
    });

    it("should not set the EJS_cheats global variable when no cheat codes are available", async () => {
      // Arrange
      cheatApi.getCheatCodes.mockResolvedValue([]);

      // Delete the EJS_cheats property if it exists
      if ("EJS_cheats" in window) {
        delete window.EJS_cheats;
      }

      // Act
      wrapper = mount(Player, {
        props: {
          rom: mockRom,
          save: null,
          state: null,
          bios: null,
          core: "nes",
          disc: null,
        },
        global: {
          plugins: [pinia],
          stubs: {
            // Stub any components or directives as needed
          },
          provide: {
            emitter: {
              on: jest.fn(),
              off: jest.fn(),
              emit: jest.fn(),
            },
          },
        },
      });

      // Wait for promises to resolve
      await flushPromises();

      // Assert
      expect(window.EJS_cheats).toBeUndefined();
    });
  });

  describe("Integration with fetchCheatCodes function", () => {
    it("should call getCheatCodes with the correct ROM ID", async () => {
      // Arrange
      cheatApi.getCheatCodes.mockResolvedValue(mockCheatCodes);

      // Act
      wrapper = mount(Player, {
        props: {
          rom: mockRom,
          save: null,
          state: null,
          bios: null,
          core: "nes",
          disc: null,
        },
        global: {
          plugins: [pinia],
          stubs: {
            // Stub any components or directives as needed
          },
          provide: {
            emitter: {
              on: jest.fn(),
              off: jest.fn(),
              emit: jest.fn(),
            },
          },
        },
      });

      // Wait for promises to resolve
      await flushPromises();

      // Assert
      expect(cheatApi.getCheatCodes).toHaveBeenCalledWith("123");
    });
  });
});
