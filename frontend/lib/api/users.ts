import { authFetch } from "@/lib/auth/session";

export type UserProfile = {
  current_role: string | null;
  career_level: string | null;
  years_of_experience: number | null;
  updated_at: string | null;
};

export type UserProfileInput = Omit<UserProfile, "updated_at">;

type CurrentUser = {
  id: string;
  email: string;
  created_at: string;
  updated_at: string;
  profile: UserProfile;
};

export type ApiResult<T> =
  | { ok: true; data: T }
  | { ok: false; error: string; unauthorized?: boolean };

const SESSION_EXPIRED_MESSAGE =
  "Your session has expired. Please sign in again.";
const PROFILE_LOAD_FAILED_MESSAGE =
  "We could not load your profile. The CareerIQ API may not be running.";
const PROFILE_SAVE_FAILED_MESSAGE =
  "We could not save your profile. Your changes are still here — try again.";

async function request<T>(
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

  try {
    return { ok: true, data: (await response.json()) as T };
  } catch {
    return { ok: false, error: failureMessage };
  }
}

export function fetchCurrentUser(): Promise<ApiResult<CurrentUser>> {
  return request<CurrentUser>(
    "/api/users/me",
    { cache: "no-store" },
    PROFILE_LOAD_FAILED_MESSAGE,
  );
}

export function saveUserProfile(
  profile: UserProfileInput,
): Promise<ApiResult<UserProfile>> {
  return request<UserProfile>(
    "/api/users/me/profile",
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(profile),
    },
    PROFILE_SAVE_FAILED_MESSAGE,
  );
}
