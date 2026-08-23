import { authFetch } from "@/lib/auth/session";

export type ApiResult<T> =
  | { ok: true; data: T }
  | { ok: false; error: string; unauthorized?: boolean };

export const SESSION_EXPIRED_MESSAGE =
  "Your session has expired. Please sign in again.";

export async function request<T>(
  path: string,
  init: RequestInit,
  failureMessage: string,
): Promise<ApiResult<T>> {
  let response: Response;
  try {
    response = await authFetch(path, init);
  } catch {
    return { ok: false, error: failureMessage };
  }

  if (response.status === 401) {
    return { ok: false, error: SESSION_EXPIRED_MESSAGE, unauthorized: true };
  }
  if (!response.ok) {
    return { ok: false, error: failureMessage };
  }
  if (response.status === 204) {
    return { ok: true, data: undefined as T };
  }

  try {
    return { ok: true, data: (await response.json()) as T };
  } catch {
    return { ok: false, error: failureMessage };
  }
}
