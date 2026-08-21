import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { LoginForm } from "@/components/auth/login-form";
import { SessionStatus } from "@/components/auth/session-status";
import { AuthProvider } from "@/lib/auth/context";

const push = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

const TOKEN = "access-token-one";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function stubFetch(handler: (url: string) => Response | Promise<Response>) {
  const mock = vi.fn((input: RequestInfo | URL) =>
    Promise.resolve(handler(String(input))),
  );
  vi.stubGlobal("fetch", mock);
  return mock;
}

beforeEach(() => {
  push.mockClear();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

function signIn(email: string, password: string) {
  fireEvent.change(screen.getByLabelText("Email"), {
    target: { value: email },
  });
  fireEvent.change(screen.getByLabelText("Password"), {
    target: { value: password },
  });
  fireEvent.click(screen.getByRole("button", { name: "Sign in" }));
}

describe("login form", () => {
  it("signs in and navigates home on success", async () => {
    stubFetch((url) =>
      url.endsWith("/login")
        ? jsonResponse({ access_token: TOKEN })
        : jsonResponse({ detail: "no" }, 401),
    );
    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>,
    );

    signIn("member@example.com", "a real password");

    await waitFor(() => expect(push).toHaveBeenCalledWith("/"));
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("shows one generic error when credentials are rejected", async () => {
    stubFetch(() =>
      jsonResponse({ detail: "Incorrect email address or password." }, 401),
    );
    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>,
    );

    signIn("member@example.com", "wrong");

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Incorrect email or password.");
    expect(push).not.toHaveBeenCalled();
  });

  it("disables the button and shows progress while submitting", async () => {
    let releaseLogin: (value: Response) => void = () => {};
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        if (String(input).endsWith("/login")) {
          return new Promise<Response>((resolve) => {
            releaseLogin = resolve;
          });
        }
        return Promise.resolve(jsonResponse({ detail: "no" }, 401));
      }),
    );
    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>,
    );

    signIn("member@example.com", "a real password");

    const submitting = await screen.findByRole("button", {
      name: "Signing in…",
    });
    expect(submitting).toBeDisabled();

    releaseLogin(jsonResponse({ access_token: TOKEN }));
    await waitFor(() => expect(push).toHaveBeenCalled());
  });
});

describe("session restoration", () => {
  it("reports a signed-in session when refresh succeeds", async () => {
    stubFetch(() => jsonResponse({ access_token: TOKEN }));
    render(
      <AuthProvider>
        <SessionStatus />
      </AuthProvider>,
    );

    expect(screen.getByText("Checking…")).toBeInTheDocument();
    expect(await screen.findByText("Signed in")).toBeInTheDocument();
  });

  it("reports signed out without an error for a normal visitor", async () => {
    stubFetch(() => jsonResponse({ detail: "no" }, 401));
    render(
      <AuthProvider>
        <SessionStatus />
      </AuthProvider>,
    );

    expect(await screen.findByText("Signed out")).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("attempts restoration only once per mount", async () => {
    const mock = stubFetch(() => jsonResponse({ access_token: TOKEN }));
    render(
      <AuthProvider>
        <SessionStatus />
      </AuthProvider>,
    );

    await screen.findByText("Signed in");

    expect(
      mock.mock.calls.filter(([url]) => String(url).endsWith("/refresh")),
    ).toHaveLength(1);
  });
});

describe("sign out", () => {
  it("returns the interface to the unauthenticated state", async () => {
    stubFetch((url) =>
      url.endsWith("/logout")
        ? new Response(null, { status: 204 })
        : jsonResponse({ access_token: TOKEN }),
    );
    render(
      <AuthProvider>
        <SessionStatus />
      </AuthProvider>,
    );
    await screen.findByText("Signed in");

    fireEvent.click(screen.getByRole("button", { name: "Sign out" }));

    expect(await screen.findByText("Signed out")).toBeInTheDocument();
  });
});
