import api from "@/services/api/index";

export interface CheatType {
  id: string;
  name: string;
  description: string;
  pattern: string;
  example: string;
}

export interface CheatCode {
  id: string;
  name: string;
  code: string;
  description: string;
  type: string;
  romId: string;
}

export interface CheatFile {
  id: string;
  name: string;
  romId: string;
}

export const addRomCheat = async (romId: string, cheatCode: CheatCode) => {
  try {
    console.log(`Adding cheat code for ROM ${romId}:`, cheatCode);
    const response = await api.post(`/roms/${romId}/cheats`, cheatCode);
    console.log(`Add cheat response:`, response);
    return response.data;
  } catch (error: any) {
    console.error(`Failed to add cheat code for ROM ${romId}:`, error);
    // Log more details about the error
    if (error.response) {
      console.error("Error response:", error.response.data);
      console.error("Error status:", error.response.status);
    } else if (error.request) {
      console.error("No response received:", error.request);
    }
    throw error;
  }
};

export const updateRomCheat = async (
  romId: string,
  cheatId: string,
  cheatCode: CheatCode,
) => {
  const response = await api.put(`/roms/${romId}/cheats/${cheatId}`, cheatCode);
  return response.data;
};

export const deleteRomCheat = async (romId: string, cheatId: string) => {
  const response = await api.delete(`/roms/${romId}/cheats/${cheatId}`);
  return response.data;
};

export const getCheatCodes = async (romId: string) => {
  try {
    const response = await api.get(`/roms/${romId}/cheats`);
    return response.data;
  } catch (error) {
    console.error(`Failed to get cheat codes for ROM ${romId}:`, error);
    throw error;
  }
};

export const syncCheatCodes = async (romId: string) => {
  try {
    const response = await api.post(`/roms/${romId}/cheats/sync`);
    return response.data;
  } catch (error) {
    console.error(`Failed to synchronize cheat codes for ROM ${romId}:`, error);
    throw error;
  }
};

export const uploadCheatFile = async (romId: string, formData: FormData) => {
  const response = await api.post(`/roms/${romId}/cheat-files`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};

export const getCheatFiles = async (romId: string) => {
  const response = await api.get(`/roms/${romId}/cheat-files`);
  return response.data;
};

export const deleteCheatFile = async (romId: string, fileId: string) => {
  const response = await api.delete(`/roms/${romId}/cheat-files/${fileId}`);
  return response.data;
};

export const getCheatTypes = async () => {
  try {
    const response = await api.get("/cheat_types");
    return response.data;
  } catch (error) {
    console.error("Failed to get cheat types:", error);
    throw error;
  }
};

export const getCheatType = async (typeId: string) => {
  try {
    const response = await api.get(`/cheat_types/${typeId}`);
    return response.data;
  } catch (error) {
    console.error(`Failed to get cheat type ${typeId}:`, error);
    throw error;
  }
};
