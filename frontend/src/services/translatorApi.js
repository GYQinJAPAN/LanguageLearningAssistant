import { API_ENDPOINTS } from "../config/api";

function formatDetail(detail) {
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const location = Array.isArray(item.loc) ? item.loc.join(".") : "";
        return location ? `${location}: ${item.msg}` : item.msg;
      })
      .filter(Boolean)
      .join("; ");
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
      ? `Server returned a non-JSON response: ${text.slice(0, 120)}`
      : "Server returned a non-JSON response."
  );
}

function buildHttpError(response, data, fallbackMessage) {
  const detail = formatDetail(data?.detail);

  if (response.status === 422) {
    return detail || "Request validation failed. Please check your input.";
  }

  if (response.status >= 500) {
    return detail || "Server error. Please try again later.";
  }

  return detail || fallbackMessage || `Request failed. HTTP ${response.status}.`;
}

async function requestJson(url, options, fallbackMessage) {
  let response;

  try {
    response = await fetch(url, options);
  } catch {
    throw new Error("Cannot connect to the backend service. Confirm FastAPI is running.");
  }

  const data = await parseJsonResponse(response);

  if (!response.ok) {
    throw new Error(buildHttpError(response, data, fallbackMessage));
  }

  return data;
}

export async function fetchStyles() {
  return requestJson(API_ENDPOINTS.styles, undefined, "Failed to load styles.");
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
    "Translation request failed."
  );
}

export async function fetchHistory({ page = 1, pageSize = 10, q = "" } = {}) {
  const url = new URL(API_ENDPOINTS.history);
  url.searchParams.set("page", String(page));
  url.searchParams.set("page_size", String(pageSize));

  if (q.trim()) {
    url.searchParams.set("q", q.trim());
  }

  return requestJson(url.toString(), undefined, "Failed to load history.");
}

export async function fetchHistoryDetail(id) {
  return requestJson(`${API_ENDPOINTS.history}/${id}`, undefined, "Failed to load history detail.");
}
