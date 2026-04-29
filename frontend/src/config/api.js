const rawBaseUrl = import.meta.env.VITE_API_BASE_URL;

function normalizeBaseUrl(value) {
  const baseUrl = value?.trim();

  if (!baseUrl) {
    throw new Error("缺少 VITE_API_BASE_URL，请检查前端 .env 配置。");
  }

  return baseUrl.replace(/\/+$/, "");
}

function joinUrl(baseUrl, path) {
  return `${baseUrl}/${path.replace(/^\/+/, "")}`;
}

export const API_BASE_URL = normalizeBaseUrl(rawBaseUrl);

export const API_ENDPOINTS = {
  styles: joinUrl(API_BASE_URL, "styles"),
  translate: joinUrl(API_BASE_URL, "translate"),
  history: joinUrl(API_BASE_URL, "history"),
  variantSpeakingTips: (variantId) =>
    joinUrl(API_BASE_URL, `variants/${variantId}/speaking-tips`),
};
