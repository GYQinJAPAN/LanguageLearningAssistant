import { API_ENDPOINTS } from "../config/api";

function formatDetail(detail) {
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const location = Array.isArray(item.loc) ? item.loc.join(".") : "";
        return location ? `${location}: ${item.msg}` : item.msg;
      })
      .filter(Boolean)
      .join("；");
  }

  if (typeof detail === "string") {
    return detail;
  }

  if (detail && typeof detail === "object") {
    return detail.message || JSON.stringify(detail);
  }

  return "";
}

async function parseJsonResponse(response) {
  const contentType = response.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    return response.json();
  }

  const text = await response.text();
  throw new Error(
    text
      ? `服务返回了非 JSON 响应：${text.slice(0, 120)}`
      : "服务返回了非 JSON 响应。"
  );
}

function buildHttpError(response, data, fallbackMessage) {
  const detail = formatDetail(data?.detail);

  if (response.status === 422) {
    return detail || "请求参数校验失败，请检查输入内容。";
  }

  if (response.status >= 500) {
    return detail || "服务器内部错误，请稍后再试。";
  }

  return detail || fallbackMessage || `请求失败（HTTP ${response.status}）`;
}

async function requestJson(url, options, fallbackMessage) {
  let response;

  try {
    response = await fetch(url, options);
  } catch {
    throw new Error("无法连接后端服务，请确认 FastAPI 已启动。");
  }

  const data = await parseJsonResponse(response);

  if (!response.ok) {
    throw new Error(buildHttpError(response, data, fallbackMessage));
  }

  return data;
}

export async function fetchStyles() {
  return requestJson(API_ENDPOINTS.styles, undefined, "获取风格列表失败。");
}

export async function translateText(payload) {
  return requestJson(
    API_ENDPOINTS.translate,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    },
    "翻译请求失败。"
  );
}
