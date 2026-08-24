import { authFetch } from "@/lib/auth/session";

export type ApiResult<T> =
  | { ok: true; data: T }
  | { ok: false; error: string; unauthorized?: boolean; notFound?: boolean };

export const SESSION_EXPIRED_MESSAGE =
  "Your session has expired. Please sign in again.";
export const NOT_FOUND_MESSAGE = "We could not find what you were looking for.";

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
  if (response.status === 404) {
    return { ok: false, error: NOT_FOUND_MESSAGE, notFound: true };
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
