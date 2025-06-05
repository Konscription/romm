<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { useTheme } from "vuetify";
import { storeToRefs } from "pinia";
//import cheatApi from "@/services/api/cheats"; // hypothetical API
import romApi from "@/services/api/rom";
import storeAuth from "@/stores/auth";
import type { DetailedRom } from "@/stores/roms";

const props = defineProps<{ rom: DetailedRom }>();
const { t } = useI18n();
const theme = useTheme();
const auth = storeAuth();
const newCheatFile = ref<File | null>(null);
const { scopes } = storeToRefs(auth);

const cheats = ref(
  (props.rom.cheats ?? []).map((cheat) => ({
    ...cheat,
    isEditing: false,
    editName: cheat.name,
    editCode: cheat.code,
    editDescription: cheat.description,
  })),
);

const newCheat = ref({
  name: "",
  code: "",
  description: "",
});

async function addCheat() {
  if (!newCheat.value.name || !newCheat.value.code) return;

  const result = await romApi.addRomCheat({
    romId: props.rom.id,
    data: { ...newCheat.value },
  });

  if (result?.id) {
    cheats.value.push({
      ...result,
      isEditing: false,
      editName: result.name,
      editCode: result.code,
      editDescription: result.description,
    });
    newCheat.value = { name: "", code: "", description: "" };
  }
}

function toggleEdit(cheat: any) {
  cheat.isEditing = !cheat.isEditing;
}

async function saveEdit(cheat: any) {
  const updated = {
    name: cheat.editName,
    code: cheat.editCode,
    description: cheat.editDescription,
  };

  const result = await romApi.updateRomCheat({
    romId: props.rom.id,
    cheatId: cheat.id,
    data: updated,
  });

  if (result) {
    cheat.name = updated.name;
    cheat.code = updated.code;
    cheat.description = updated.description;
    cheat.isEditing = false;
  }
}

async function deleteCheat(cheatId: number) {
  if (!confirm(t("cheat.confirmDelete"))) return;

  const success = await romApi.deleteRomCheat({
    romId: props.rom.id,
    cheatId,
  });

  if (success) {
    cheats.value = cheats.value.filter((c: { id: number }) => c.id !== cheatId);
  }
}

async function uploadCheatFile() {
  if (!newCheatFile.value || !props.rom.id) return;

  const formData = new FormData();
  formData.append("file", newCheatFile.value);

  try {
    await cheatApi.uploadCheatFile(props.rom.id, formData);
    await refreshCheatFiles(); // fetch updated file list
    newCheatFile.value = null;
  } catch (err) {
    // Handle Error
  }
}

async function deleteCheatFile(fileId: number) {
  try {
    await cheatApi.deleteCheatFile(props.rom.id, fileId);
    await refreshCheatFiles();
  } catch (err) {
    // Handle Error
  }
}

// Reload cheat file list after upload/delete
async function refreshCheatFiles() {
  try {
    const { data } = await cheatApi.getCheatFiles(props.rom.id);
    props.rom.cheat_files = data;
  } catch {
    // Handle Error
  }
}

function formatBytes(bytes: number): string {
  if (!bytes) return "0 B";
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
}

function formatDate(date: string): string {
  return new Date(date).toLocaleDateString();
}
</script>

<template>
  <!-- Cheats File Info Box -->
  <v-card
    v-if="props.rom.cheat_files?.length"
    class="mb-4"
    outlined
    rounded="lg"
  >
    <v-card-title>{{ t("rom.cheatFilesTitle") }}</v-card-title>
    <v-divider />
    <v-card-text>
      <!-- Upload Cheat File -->
      <v-file-input
        v-model="newCheatFile"
        :label="t('rom.uploadCheatFile')"
        accept=".txt,.db,.zip"
        show-size
        dense
        outlined
        prepend-icon="mdi-upload"
        @change="uploadCheatFile"
      />

      <v-list>
        <v-list-item
          v-for="(file, index) in props.rom.cheat_files"
          :key="index"
          class="px-0"
        >
          <v-list-item-content>
            <v-list-item-title class="font-weight-medium">
              {{ file.name }}
            </v-list-item-title>
            <v-list-item-subtitle>
              {{ formatBytes(file.size) }} – {{ formatDate(file.updated_at) }}
            </v-list-item-subtitle>
          </v-list-item-content>

          <v-list-item-action>
            <v-btn
              icon
              color="primary"
              :href="file.path"
              target="_blank"
              :title="t('common.view')"
            >
              <v-icon>mdi-open-in-new</v-icon>
            </v-btn>

            <v-btn
              icon
              color="error"
              @click="deleteCheatFile(file.id)"
              :title="t('common.delete')"
            >
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </v-list-item-action>
        </v-list-item>
      </v-list>
    </v-card-text>
  </v-card>

  <v-card class="mt-4">
    <v-card-title class="bg-toplayer">
      <v-list-item class="pl-2 pr-0">
        <span class="text-h6">{{ t("rom.cheats") }}</span>
      </v-list-item>
    </v-card-title>

    <v-card-text class="pa-4">
      <v-table>
        <thead>
          <tr>
            <th>{{ t("cheat.name") }}</th>
            <th>{{ t("cheat.code") }}</th>
            <th>{{ t("cheat.description") }}</th>
            <th class="text-center">{{ t("common.actions") }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cheat in cheats" :key="cheat.id">
            <td>
              <template v-if="cheat.isEditing">
                <v-text-field
                  v-model="cheat.editName"
                  density="compact"
                  variant="outlined"
                  hide-details
                />
              </template>
              <template v-else>
                {{ cheat.name }}
              </template>
            </td>
            <td>
              <template v-if="cheat.isEditing">
                <v-text-field
                  v-model="cheat.editCode"
                  density="compact"
                  variant="outlined"
                  hide-details
                />
              </template>
              <template v-else>
                <code>{{ cheat.code }}</code>
              </template>
            </td>
            <td>
              <template v-if="cheat.isEditing">
                <v-text-field
                  v-model="cheat.editDescription"
                  density="compact"
                  variant="outlined"
                  hide-details
                />
              </template>
              <template v-else>
                {{ cheat.description }}
              </template>
            </td>
            <td class="text-center">
              <v-btn
                icon
                density="comfortable"
                @click="cheat.isEditing ? saveEdit(cheat) : toggleEdit(cheat)"
                :disabled="!scopes.includes('roms.user.write')"
              >
                <v-icon>
                  {{ cheat.isEditing ? "mdi-check" : "mdi-pencil" }}
                </v-icon>
              </v-btn>
              <v-btn
                icon
                density="comfortable"
                color="error"
                @click="deleteCheat(cheat.id)"
                :disabled="!scopes.includes('roms.user.write')"
              >
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </td>
          </tr>
        </tbody>
      </v-table>

      <v-divider class="my-4" />

      <v-row class="align-center">
        <v-col cols="12" md="3">
          <v-text-field
            v-model="newCheat.name"
            :label="t('cheat.name')"
            density="compact"
            variant="outlined"
            hide-details
          />
        </v-col>
        <v-col cols="12" md="3">
          <v-text-field
            v-model="newCheat.code"
            :label="t('cheat.code')"
            density="compact"
            variant="outlined"
            hide-details
          />
        </v-col>
        <v-col cols="12" md="4">
          <v-text-field
            v-model="newCheat.description"
            :label="t('cheat.description')"
            density="compact"
            variant="outlined"
            hide-details
          />
        </v-col>
        <v-col cols="12" md="2">
          <v-btn
            color="primary"
            block
            :disabled="!newCheat.name || !newCheat.code"
            @click="addCheat"
          >
            {{ t("cheat.add") }}
          </v-btn>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<style scoped>
thead th {
  text-align: left;
  font-weight: 600;
  padding: 8px;
}

tbody td {
  padding: 8px;
  border-top: 1px solid #ddd;
  vertical-align: top;
}
</style>
