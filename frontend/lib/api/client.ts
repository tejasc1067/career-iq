export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type ApiHealth = {
  status: string;
  service: string;
  version: string;
};

export type HealthResult =
  | { ok: true; health: ApiHealth }
  | { ok: false; error: string };

export async function fetchApiHealth(): Promise<HealthResult> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      cache: "no-store",
      signal: AbortSignal.timeout(3000),
    });

    if (!response.ok) {
      return { ok: false, error: `API responded with ${response.status}` };
    }

    return { ok: true, health: (await response.json()) as ApiHealth };
  } catch {
    return { ok: false, error: `No response from ${API_BASE_URL}` };
  }
}
