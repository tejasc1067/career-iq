import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import Home from "@/app/page";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("home page", () => {
  it("confirms the frontend is running and reports a reachable API", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            status: "ok",
            service: "careeriq-api",
            version: "0.1.0",
          }),
          { status: 200 },
        ),
      ),
    );

    render(await Home());

    expect(screen.getByText("CareerIQ")).toBeInTheDocument();
    expect(screen.getByText("Running")).toBeInTheDocument();
    expect(screen.getByText(/Reachable/)).toBeInTheDocument();
  });

  it("reports an unreachable API without failing to render", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("down")));

    render(await Home());

    expect(screen.getByText("Unreachable")).toBeInTheDocument();
  });
});
