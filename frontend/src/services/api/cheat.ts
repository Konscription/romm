import api from "@/services/api/index";

export interface CheatCode {
  id: string;
  code: string;
  description: string;
  romId: string;
}

export interface CheatFile {
  id: string;
  name: string;
  romId: string;
}

export const addRomCheat = async (romId: string, cheatCode: CheatCode) => {
  const response = await api.post(`/roms/${romId}/cheats`, cheatCode);
  return response.data;
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
  const response = await api.get(`/roms/${romId}/cheats`);
  return response.data;
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
