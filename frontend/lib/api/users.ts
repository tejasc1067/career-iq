import { request, type ApiResult } from "@/lib/api/request";

export type { ApiResult };

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

const PROFILE_LOAD_FAILED_MESSAGE =
  "We could not load your profile. The CareerIQ API may not be running.";
const PROFILE_SAVE_FAILED_MESSAGE =
  "We could not save your profile. Your changes are still here — try again.";

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
