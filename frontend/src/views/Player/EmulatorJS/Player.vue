<script setup lang="ts">
import type { FirmwareSchema, SaveSchema, StateSchema } from "@/__generated__";
import { saveApi as api } from "@/services/api/save";
import storeRoms, { type DetailedRom } from "@/stores/roms";
import {
  areThreadsRequiredForEJSCore,
  getSupportedEJSCores,
  getControlSchemeForPlatform,
  getDownloadPath,
} from "@/utils";
import { inject, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useTheme } from "vuetify";
import {
  saveSave,
  saveState,
  loadEmulatorJSSave,
  loadEmulatorJSState,
  createQuickLoadButton,
  createSaveQuitButton,
} from "./utils";
import type { Emitter } from "mitt";
import type { Events } from "@/types/emitter";
import storePlaying from "@/stores/playing";
import { storeToRefs } from "pinia";
import { getCheatCodes } from "@/services/api/cheat";
import { onBeforeRouteLeave } from "vue-router";

const INVALID_CHARS_REGEX = /[#<$+%>!`&*'|{}/\\?"=@:^\r\n]/gi;

const romsStore = storeRoms();
const props = defineProps<{
  rom: DetailedRom;
  save: SaveSchema | null;
  state: StateSchema | null;
  bios: FirmwareSchema | null;
  core: string | null;
  disc: number | null;
}>();
const romRef = ref<DetailedRom>(props.rom);
const saveRef = ref<SaveSchema | null>(props.save);
const theme = useTheme();
const emitter = inject<Emitter<Events>>("emitter");
const playingStore = storePlaying();
const { playing, fullScreen } = storeToRefs(playingStore);

// Declare global variables for EmulatorJS
declare global {
  interface Window {
    EJS_core: string;
    EJS_biosUrl: string;
    EJS_player: string;
    EJS_pathtodata: string;
    EJS_color: string;
    EJS_defaultOptions: object;
    EJS_gameID: number;
    EJS_gameName: string;
    EJS_backgroundImage: string;
    EJS_backgroundColor: string;
    EJS_gameUrl: string;
    EJS_loadStateURL: string | null;
    EJS_cheats: Array<[string, string]>;
    EJS_gameParentUrl: string;
    EJS_gamePatchUrl: string;
    EJS_netplayServer: string;
    EJS_alignStartButton: "top" | "center" | "bottom";
    EJS_startOnLoaded: boolean;
    EJS_fullscreenOnLoaded: boolean;
    EJS_threads: boolean;
    EJS_controlScheme: string | null;
    EJS_emulator: any; // eslint-disable-line @typescript-eslint/no-explicit-any
    EJS_Buttons: Record<string, boolean>;
    EJS_VirtualGamepadSettings: {};
    EJS_onGameStart: () => void;
    EJS_onSaveState: (args: {
      screenshot: Uint8Array;
      state: Uint8Array;
    }) => void;
    EJS_onLoadState: () => void;
    EJS_onSaveSave: (args: {
      screenshot: Uint8Array;
      save: Uint8Array;
    }) => void;
    EJS_onLoadSave: () => void;
  }
}

const supportedCores = getSupportedEJSCores(romRef.value.platform_slug);
window.EJS_core =
  supportedCores.find((core) => core === props.core) ?? supportedCores[0];
window.EJS_controlScheme = getControlSchemeForPlatform(
  romRef.value.platform_slug,
);
window.EJS_threads = areThreadsRequiredForEJSCore(window.EJS_core);
window.EJS_gameID = romRef.value.id;
window.EJS_gameUrl = getDownloadPath({
  rom: romRef.value,
  fileIDs: props.disc ? [props.disc] : [],
});
window.EJS_biosUrl = props.bios
  ? `/api/firmware/${props.bios.id}/content/${props.bios.file_name}`
  : "";
window.EJS_player = "#game";
window.EJS_color = "#A453FF";
window.EJS_alignStartButton = "center";
window.EJS_startOnLoaded = true;
window.EJS_backgroundImage = `${window.location.origin}/assets/emulatorjs/powered_by_emulatorjs.png`;
window.EJS_backgroundColor = theme.current.value.colors.background;
// Clear any existing cheats first to prevent caching issues
window.EJS_cheats = [];

// Force saving saves and states to the browser
window.EJS_defaultOptions = {
  "save-state-location": "browser",
  rewindEnabled: "enabled",
};
// Set a valid game name
window.EJS_gameName = romRef.value.fs_name_no_tags
  .replace(INVALID_CHARS_REGEX, "")
  .trim();

// We'll load cheat codes in onMounted instead of IIFE to ensure they're refreshed on component reuse

// Function to load and refresh cheat codes
async function loadCheatCodes() {
  try {
    // Clear any existing cheats first to prevent caching issues
    window.EJS_cheats = [];
    const cheatCodes = await fetchCheatCodes();
    if (cheatCodes.length > 0) {
      // Format cheat codes for EmulatorJS
      window.EJS_cheats = formatCheatCodesForEmulatorJS(cheatCodes);
      console.log("Cheat codes loaded:", window.EJS_cheats);
    }
  } catch (error) {
    console.error("Error loading cheat codes:", error);
    displayMessage("Failed to load cheat codes", {
      duration: 4000,
      className: "msg-error",
      icon: "mdi-alert-circle-outline",
    });
  }
}

onMounted(async () => {
  window.scrollTo(0, 0);
  if (props.bios) {
    localStorage.setItem(
      `player:${romRef.value.platform_slug}:bios_id`,
      props.bios.id.toString(),
    );
  } else {
    localStorage.removeItem(`player:${romRef.value.platform_slug}:bios_id`);
  }

  if (props.core) {
    localStorage.setItem(
      `player:${romRef.value.platform_slug}:core`,
      props.core,
    );
  } else {
    localStorage.removeItem(`player:${romRef.value.platform_slug}:core`);
  }

  if (props.disc) {
    localStorage.setItem(
      `player:${romRef.value.id}:disc`,
      props.disc.toString(),
    );
  } else {
    localStorage.removeItem(`player:${romRef.value.id}:disc`);
  }

  // Load cheat codes when component is mounted
  await loadCheatCodes();

  emitter?.on("saveSelected", loadSave);
  emitter?.on("stateSelected", loadState);
});

// Watch for changes to the ROM ID and refresh cheats if it changes
watch(
  () => romRef.value.id,
  async (newId: number, oldId: number) => {
    if (newId !== oldId) {
      await loadCheatCodes();
    }
  },
);

// Reference to the timeout for cheat updates
const cheatUpdateTimeout = ref<number | null>(null);

onBeforeUnmount(async () => {
  // Clear any pending timeouts
  if (cheatUpdateTimeout.value !== null) {
    clearTimeout(cheatUpdateTimeout.value);
    cheatUpdateTimeout.value = null;
  }

  emitter?.off("saveSelected", loadSave);
  emitter?.off("stateSelected", loadState);

  fullScreen.value = false;
  playing.value = false;
});

function displayMessage(
  message: string,
  {
    duration,
    className = "msg-info",
    icon = "",
  }: {
    duration: number;
    className?: "msg-info" | "msg-error" | "msg-success";
    icon?: string;
  },
) {
  window.EJS_emulator.displayMessage(message, duration);
  const element = document.querySelector("#game .ejs_message");
  if (element) {
    element.classList.add(className, icon);
    setTimeout(() => {
      element.classList.remove(className, icon);
    }, duration);
  }
}

// Saves management
async function loadSave(save: SaveSchema) {
  saveRef.value = save;

  const { data } = await api.get(save.download_path.replace("/api", ""), {
    responseType: "arraybuffer",
  });
  if (data) {
    loadEmulatorJSSave(new Uint8Array(data));
    displayMessage("Save loaded from server", {
      duration: 3000,
      icon: "mdi-cloud-download-outline",
    });
    return;
  }

  const file = await window.EJS_emulator.selectFile();
  loadEmulatorJSSave(new Uint8Array(await file.arrayBuffer()));
}

window.EJS_onLoadSave = async function () {
  window.EJS_emulator.pause();
  window.EJS_emulator.toggleFullscreen(false);
  emitter?.emit("selectSaveDialog", romRef.value);
};

window.EJS_onSaveSave = async function ({
  save: saveFile,
  screenshot: screenshotFile,
}) {
  const save = await saveSave({
    rom: romRef.value,
    save: saveRef.value,
    saveFile,
    screenshotFile,
  });

  romsStore.update(romRef.value);

  if (save) {
    displayMessage("Save synced with server", {
      duration: 4000,
      icon: "mdi-cloud-sync",
    });
  } else {
    displayMessage("Error syncing save with server", {
      duration: 4000,
      className: "msg-error",
      icon: "mdi-sync-alert",
    });
  }
};

// States management
async function loadState(state: StateSchema) {
  const { data } = await api.get(state.download_path.replace("/api", ""), {
    responseType: "arraybuffer",
  });
  if (data) {
    loadEmulatorJSState(new Uint8Array(data));
    displayMessage("State loaded from server", {
      duration: 3000,
      icon: "mdi-cloud-download-outline",
    });
    return;
  }

  const file = await window.EJS_emulator.selectFile();
  loadEmulatorJSState(new Uint8Array(await file.arrayBuffer()));
}

window.EJS_onLoadState = async function () {
  window.EJS_emulator.pause();
  window.EJS_emulator.toggleFullscreen(false);
  emitter?.emit("selectStateDialog", romRef.value);
};

window.EJS_onSaveState = async function ({
  state: stateFile,
  screenshot: screenshotFile,
}) {
  const state = await saveState({
    rom: romRef.value,
    stateFile,
    screenshotFile,
  });
  window.EJS_emulator.storage.states.put(
    window.EJS_emulator.getBaseFileName() + ".state",
    stateFile,
  );

  romsStore.update(romRef.value);

  if (state) {
    displayMessage("State synced with server", {
      duration: 4000,
      icon: "mdi-cloud-sync",
    });
  } else {
    displayMessage("Error syncing state with server", {
      duration: 4000,
      className: "msg-error",
      icon: "mdi-sync-alert",
    });
  }
};

window.EJS_onGameStart = async () => {
  setTimeout(async () => {
    if (props.save) await loadSave(props.save);
    if (props.state) await loadState(props.state);

    window.EJS_emulator.settings = {
      ...window.EJS_emulator.settings,
      "save-state-location": "browser",
    };

    // Refresh cheat codes when game starts to ensure we have the latest
    await loadCheatCodes();

    // Clear any existing timeout
    if (cheatUpdateTimeout.value !== null) {
      clearTimeout(cheatUpdateTimeout.value);
    }

    // Wait a moment for the emulator to fully initialize before updating cheats
    // Store the timeout ID so we can clear it if needed
    cheatUpdateTimeout.value = window.setTimeout(() => {
      // Directly update the emulator's cheat system
      updateEmulatorCheats();
      cheatUpdateTimeout.value = null;
    }, 1000) as unknown as number;
  }, 10);

  const quickLoad = createQuickLoadButton();
  quickLoad.addEventListener("click", () => {
    if (
      window.EJS_emulator.settings["save-state-location"] === "browser" &&
      window.EJS_emulator.saveInBrowserSupported()
    ) {
      window.EJS_emulator.storage.states
        .get(window.EJS_emulator.getBaseFileName() + ".state")
        .then((e: Uint8Array) => {
          window.EJS_emulator.gameManager.loadState(e);
          displayMessage("Quick load from server", {
            duration: 3000,
            icon: "mdi-flash",
          });
        });
    }
  });

  const saveAndQuit = createSaveQuitButton();
  saveAndQuit.addEventListener("click", async () => {
    if (!romRef.value || !window.EJS_emulator) return window.history.back();

    const stateFile = window.EJS_emulator.gameManager.getState();
    const saveFile = window.EJS_emulator.gameManager.getSaveFile();
    const screenshotFile = await window.EJS_emulator.gameManager.screenshot();

    // Force a save of the current state
    await saveState({
      rom: romRef.value,
      stateFile,
      screenshotFile,
    });

    // Force a save of the save file
    await saveSave({
      rom: romRef.value,
      save: saveRef.value,
      saveFile,
      screenshotFile,
    });

    romsStore.update(romRef.value);
    window.history.back();
  });
};

/**
 * Retrieves cheat codes for the current ROM from the backend
 */
async function fetchCheatCodes() {
  try {
    const cheatCodes = await getCheatCodes(romRef.value.id.toString());
    console.log("Fetched cheat codes:", cheatCodes);
    return cheatCodes || [];
  } catch (error) {
    console.error("Error fetching cheat codes:", error);
    displayMessage("Failed to fetch cheat codes from server", {
      duration: 4000,
      className: "msg-error",
      icon: "mdi-alert-circle-outline",
    });
    return [];
  }
}

/**
 * Type definition for cheat codes based on the API response
 */
interface CheatCode {
  id: string;
  name: string;
  code: string;
  description: string;
  type: string;
  romId: string;
}

/**
 * Formats cheat codes for EmulatorJS
 * @param cheatCodes - Array of cheat codes to format
 * @returns Formatted cheat codes string for EmulatorJS in the format [["name", "value"], ["name2", "value2"]]
 */
function formatCheatCodesForEmulatorJS(
  cheatCodes: CheatCode[],
): Array<[string, string]> {
  if (!cheatCodes || cheatCodes.length === 0) {
    return [];
  }

  console.log("Formatting cheat codes for EmulatorJS:", cheatCodes);

  // Create an array of arrays where each inner array contains [name, code]
  return cheatCodes.map((code) => [code.name, code.code]);
}

/**
 * Directly updates the emulator's cheat system using the internal EmulatorJS methods
 * This ensures cheats are properly applied to the game
 */
function updateEmulatorCheats() {
  if (!window.EJS_emulator?.gameManager) {
    console.log("Cannot update emulator cheats: emulator not initialized");
    return;
  }

  try {
    console.log("Updating emulator cheats directly");

    // Reset existing cheats first
    window.EJS_emulator.gameManager.resetCheat();

    // Only proceed if the emulator is still available and has the necessary methods
    if (!window.EJS_emulator || !window.EJS_emulator.gameManager) {
      console.log(
        "Emulator or gameManager not available, skipping cheat update",
      );
      return;
    }

    try {
      // Convert window.EJS_cheats format to the format expected by the emulator
      interface EmulatorCheat {
        desc: string;
        code: string;
        checked: boolean;
      }

      const cheats: EmulatorCheat[] = [];
      if (window.EJS_cheats && window.EJS_cheats.length > 0) {
        window.EJS_cheats.forEach(([desc, code]) => {
          cheats.push({
            desc,
            code,
            checked: false,
          });
        });
      }

      // Check if the emulator has the necessary methods before proceeding
      if (
        typeof window.EJS_emulator.gameManager.resetCheat !== "function" ||
        typeof window.EJS_emulator.gameManager.setCheat !== "function"
      ) {
        console.log(
          "Emulator missing required cheat methods, skipping cheat update",
        );
        return;
      }

      // Reset existing cheats first
      window.EJS_emulator.gameManager.resetCheat();

      // Apply each cheat to the emulator
      cheats.forEach((cheat, index) => {
        window.EJS_emulator.gameManager.setCheat(
          index,
          cheat.checked,
          cheat.code,
        );
      });

      // Update the cheat UI if the method exists
      if (typeof window.EJS_emulator.updateCheatUI === "function") {
        window.EJS_emulator.updateCheatUI();
        console.log("Cheat UI updated successfully");
      }
    } catch (error) {
      console.error("Error during cheat update:", error);
      displayMessage("Failed to apply cheat codes", {
        duration: 4000,
        className: "msg-error",
        icon: "mdi-alert-circle-outline",
      });
    }
  } catch (error) {
    console.error("Error updating emulator cheats:", error);
    displayMessage("Failed to update emulator cheats", {
      duration: 4000,
      className: "msg-error",
      icon: "mdi-alert-circle-outline",
    });
  }
}
</script>

<template>
  <div id="game" />
</template>

<style>
#game .ejs_cheat_code {
  background-color: white;
}

#game .ejs_settings_transition {
  height: fit-content;
}

#game .ejs_game_background {
  background-size: 40%;
}

/* Hide the exit button */
#game .ejs_menu_bar .ejs_menu_button:nth-child(-1) {
  display: none;
}

#game .ejs_message {
  visibility: hidden;
  margin: 1rem;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  color: white;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  filter: opacity(0.85) drop-shadow(0 0 0.5rem rgba(0, 0, 0, 0.5));
}

#game .ejs_message::before {
  margin-right: 8px;
  font-size: 20px !important;
  font: normal normal normal 24px / 1 "Material Design Icons";
}

#game .ejs_message.msg-info {
  visibility: visible;
  background-color: rgba(var(--v-theme-romm-blue));
}

#game .ejs_message.msg-error {
  visibility: visible;
  background-color: rgba(var(--v-theme-romm-red));
}

#game .ejs_message.msg-success {
  visibility: visible;
  background-color: rgba(var(--v-theme-romm-green));
}
</style>
