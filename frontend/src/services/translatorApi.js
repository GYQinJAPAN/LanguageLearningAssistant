import { API_BASE_URL } from "../config/api";

export async function fetchStyles() {
  const response = await fetch(`${API_BASE_URL}/styles`);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "获取风格列表失败");
  }

  return data;
}

export async function translateText(payload) {
  const response = await fetch(`${API_BASE_URL}/translate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "请求失败");
  }

  return data;
}