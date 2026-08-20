import { API_BASE_URL } from "@/lib/api/client";

export type LoginOutcome = { ok: true } | { ok: false; message: string };

export const INVALID_CREDENTIALS_MESSAGE = "Incorrect email or password.";
export const UNEXPECTED_ERROR_MESSAGE =
  "Something went wrong. Please try again.";

let accessToken: string | null = null;
let refreshInFlight: Promise<string | null> | null = null;

function authUrl(path: string): string {
  return `${API_BASE_URL}/api/auth/${path}`;
}

export function getAccessToken(): string | null {
  return accessToken;
}

export function clearAccessToken(): void {
  accessToken = null;
}

async function readAccessToken(response: Response): Promise<string | null> {
  try {
    const body = (await response.json()) as { access_token?: unknown };
    return typeof body.access_token === "string" ? body.access_token : null;
  } catch {
    return null;
  }
}

export async function login(
  email: string,
  password: string,
): Promise<LoginOutcome> {
  let response: Response;
  try {
    response = await fetch(authUrl("login"), {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
  } catch {
    return { ok: false, message: UNEXPECTED_ERROR_MESSAGE };
  }

  if (response.status === 401) {
    return { ok: false, message: INVALID_CREDENTIALS_MESSAGE };
  }
  if (!response.ok) {
    return { ok: false, message: UNEXPECTED_ERROR_MESSAGE };
  }

  accessToken = await readAccessToken(response);
  return accessToken
    ? { ok: true }
    : { ok: false, message: UNEXPECTED_ERROR_MESSAGE };
}

async function requestRefresh(): Promise<string | null> {
  try {
    const response = await fetch(authUrl("refresh"), {
      method: "POST",
      credentials: "include",
    });
    accessToken = response.ok ? await readAccessToken(response) : null;
  } catch {
    accessToken = null;
  }
  return accessToken;
}

export function refreshSession(): Promise<string | null> {
  refreshInFlight ??= requestRefresh().finally(() => {
    refreshInFlight = null;
  });
  return refreshInFlight;
}

export async function logout(): Promise<void> {
  await fetch(authUrl("logout"), {
    method: "POST",
    credentials: "include",
  }).catch(() => null);
  accessToken = null;
}

function withToken(init: RequestInit, token: string | null): RequestInit {
  const headers = new Headers(init.headers);
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  return { ...init, credentials: "include", headers };
}

export async function authFetch(
  path: string,
  init: RequestInit = {},
): Promise<Response> {
  const response = await fetch(
    `${API_BASE_URL}${path}`,
    withToken(init, accessToken),
  );
  if (response.status !== 401) {
    return response;
  }

  const refreshed = await refreshSession();
  if (!refreshed || init.body instanceof ReadableStream) {
    return response;
  }

  return fetch(`${API_BASE_URL}${path}`, withToken(init, refreshed));
}
