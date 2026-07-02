/**
 * API service layer — all HTTP calls go through here.
 * Keeps components decoupled from axios / endpoint URLs.
 */

import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30_000,
});

/**
 * POST /api/register
 *
 * @param {File}   file       - The image file to register
 * @param {string} modelName  - The AI model that generated the image
 * @returns {Promise<Object>} - The registration response from the API
 */
export async function registerMedia(file, modelName) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("model_name", modelName);

  const { data } = await api.post("/api/register", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return data;
}

export default api;
