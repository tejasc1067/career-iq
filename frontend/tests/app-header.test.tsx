import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AppHeader } from "@/components/navigation/app-header";
import { AuthProvider } from "@/lib/auth/context";

const pathname = vi.fn(() => "/");
vi.mock("next/navigation", () => ({
  usePathname: () => pathname(),
}));

afterEach(() => {
  vi.unstubAllGlobals();
});

function renderHeader() {
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
  render(
    <AuthProvider>
      <AppHeader />
    </AuthProvider>,
  );
}

describe("app header", () => {
  it("links to the profile page", () => {
    pathname.mockReturnValue("/");
    renderHeader();

    expect(screen.getByRole("link", { name: "My Profile" })).toHaveAttribute(
      "href",
      "/profile",
    );
  });

  it("links to the resumes page", () => {
    pathname.mockReturnValue("/");
    renderHeader();

    expect(screen.getByRole("link", { name: "My resumes" })).toHaveAttribute(
      "href",
      "/resumes",
    );
  });

  it("marks the current page for assistive technology", () => {
    pathname.mockReturnValue("/profile");
    renderHeader();

    expect(screen.getByRole("link", { name: "My Profile" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getByRole("link", { name: "Home" })).not.toHaveAttribute(
      "aria-current",
    );
  });

  it("marks the resumes page as current when it is active", () => {
    pathname.mockReturnValue("/resumes");
    renderHeader();

    expect(screen.getByRole("link", { name: "My resumes" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getByRole("link", { name: "My Profile" })).not.toHaveAttribute(
      "aria-current",
    );
  });
});
