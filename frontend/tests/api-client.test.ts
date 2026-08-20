import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchApiHealth } from "@/lib/api/client";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("fetchApiHealth", () => {
  it("returns the payload when the API responds 200", async () => {
    const health = { status: "ok", service: "careeriq-api", version: "0.1.0" };
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify(health), { status: 200 }),
      ),
    );

    const result = await fetchApiHealth();

    expect(result).toEqual({ ok: true, health });
  });

  it("reports a failure instead of throwing on a non-2xx response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response("", { status: 503 })),
    );

    const result = await fetchApiHealth();

    expect(result).toEqual({ ok: false, error: "API responded with 503" });
  });

  it("reports a failure instead of throwing when the API is unreachable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("ECONNREFUSED")));

    const result = await fetchApiHealth();

    expect(result.ok).toBe(false);
  });
});
