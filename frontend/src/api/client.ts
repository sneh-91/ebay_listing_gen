const DEFAULT_API_BASE_URL = "http://localhost:8000";

export type ApiErrorResponse = {
  detail?: unknown;
};

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(message: string, status: number, detail?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

export async function apiRequest<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL;
  const response = await fetch(`${baseUrl}${path}`, {
    credentials: "include",
    ...init,
  });

  if (!response.ok) {
    let message = "Request failed.";
    let detail: unknown;

    try {
      const payload = (await response.json()) as ApiErrorResponse;
      detail = payload.detail;
      if (typeof payload.detail === "string") {
        message = payload.detail;
      } else if (
        payload.detail &&
        typeof payload.detail === "object" &&
        "message" in payload.detail &&
        typeof payload.detail.message === "string"
      ) {
        message = payload.detail.message;
      }
    } catch {
      message = response.statusText || message;
    }

    throw new ApiError(message, response.status, detail);
  }

  return (await response.json()) as T;
}
