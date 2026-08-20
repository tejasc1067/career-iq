import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const TOKEN = "access-token-one";
const NEXT_TOKEN = "access-token-two";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

async function loadSession() {
  vi.resetModules();
  return import("@/lib/auth/session");
}

beforeEach(() => {
  vi.restoreAllMocks();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("login", () => {
  it("keeps the access token in memory and sends credentials", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(jsonResponse({ access_token: TOKEN }));
    vi.stubGlobal("fetch", fetchMock);
    const session = await loadSession();

    const outcome = await session.login("member@example.com", "a password");

    expect(outcome).toEqual({ ok: true });
    expect(session.getAccessToken()).toBe(TOKEN);
    expect(fetchMock.mock.calls[0][1]).toMatchObject({
      method: "POST",
      credentials: "include",
    });
  });

  it("reports invalid credentials without exposing server detail", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          jsonResponse({ detail: "Incorrect email address or password." }, 401),
        ),
    );
    const session = await loadSession();

    const outcome = await session.login("member@example.com", "wrong");

    expect(outcome).toEqual({
      ok: false,
      message: session.INVALID_CREDENTIALS_MESSAGE,
    });
    expect(session.getAccessToken()).toBeNull();
  });

  it("fails normally when a 2xx body cannot be parsed as JSON", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response("<html>proxy error page</html>", {
          status: 200,
          headers: { "Content-Type": "text/html" },
        }),
      ),
    );
    const session = await loadSession();

    const outcome = await session.login("member@example.com", "a password");

    expect(outcome).toEqual({
      ok: false,
      message: session.UNEXPECTED_ERROR_MESSAGE,
    });
    expect(session.getAccessToken()).toBeNull();
  });

  it("reports a generic failure when the request cannot complete", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
    const session = await loadSession();

    const outcome = await session.login("member@example.com", "a password");

    expect(outcome).toEqual({
      ok: false,
      message: session.UNEXPECTED_ERROR_MESSAGE,
    });
  });
});

describe("refreshSession", () => {
  it("restores a session when the refresh cookie is valid", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse({ access_token: TOKEN })),
    );
    const session = await loadSession();

    await expect(session.refreshSession()).resolves.toBe(TOKEN);
    expect(session.getAccessToken()).toBe(TOKEN);
  });

  it("leaves the session unauthenticated when refresh is rejected", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse({ detail: "no" }, 401)),
    );
    const session = await loadSession();

    await expect(session.refreshSession()).resolves.toBeNull();
    expect(session.getAccessToken()).toBeNull();
  });

  it("resolves to null when a 2xx refresh body cannot be parsed", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response("not json", { status: 200 })),
    );
    const session = await loadSession();

    await expect(session.refreshSession()).resolves.toBeNull();
    expect(session.getAccessToken()).toBeNull();
  });

  it("issues exactly one request for concurrent callers", async () => {
    let resolveFetch: (value: Response) => void = () => {};
    const fetchMock = vi.fn().mockImplementation(
      () =>
        new Promise<Response>((resolve) => {
          resolveFetch = resolve;
        }),
    );
    vi.stubGlobal("fetch", fetchMock);
    const session = await loadSession();

    const callers = [
      session.refreshSession(),
      session.refreshSession(),
      session.refreshSession(),
    ];
    resolveFetch(jsonResponse({ access_token: TOKEN }));
    const results = await Promise.all(callers);

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(results).toEqual([TOKEN, TOKEN, TOKEN]);
  });

  it("allows a later refresh after the in-flight one settles", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(jsonResponse({ access_token: TOKEN }));
    vi.stubGlobal("fetch", fetchMock);
    const session = await loadSession();

    await session.refreshSession();
    await session.refreshSession();

    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});

describe("authFetch", () => {
  it("retries the original request once after a successful refresh", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(new Response("", { status: 401 }))
      .mockResolvedValueOnce(jsonResponse({ access_token: NEXT_TOKEN }))
      .mockResolvedValueOnce(jsonResponse({ ok: true }));
    vi.stubGlobal("fetch", fetchMock);
    const session = await loadSession();

    const response = await session.authFetch("/api/resumes");

    expect(response.status).toBe(200);
    expect(fetchMock).toHaveBeenCalledTimes(3);
    const retryHeaders = new Headers(fetchMock.mock.calls[2][1].headers);
    expect(retryHeaders.get("Authorization")).toBe(`Bearer ${NEXT_TOKEN}`);
  });

  it("does not retry when the refresh fails", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(new Response("", { status: 401 }))
      .mockResolvedValueOnce(new Response("", { status: 401 }));
    vi.stubGlobal("fetch", fetchMock);
    const session = await loadSession();

    const response = await session.authFetch("/api/resumes");

    expect(response.status).toBe(401);
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(session.getAccessToken()).toBeNull();
  });

  it("refreshes but does not replay a stream body it cannot re-send", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(new Response("", { status: 401 }))
      .mockResolvedValueOnce(jsonResponse({ access_token: NEXT_TOKEN }));
    vi.stubGlobal("fetch", fetchMock);
    const session = await loadSession();

    const body = new ReadableStream({
      start(controller) {
        controller.enqueue(new TextEncoder().encode("chunk"));
        controller.close();
      },
    });
    const response = await session.authFetch("/api/resumes", {
      method: "POST",
      body,
    });

    expect(response.status).toBe(401);
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(session.getAccessToken()).toBe(NEXT_TOKEN);
  });

  it("replays a string body after refreshing", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(new Response("", { status: 401 }))
      .mockResolvedValueOnce(jsonResponse({ access_token: NEXT_TOKEN }))
      .mockResolvedValueOnce(jsonResponse({ ok: true }));
    vi.stubGlobal("fetch", fetchMock);
    const session = await loadSession();

    const response = await session.authFetch("/api/resumes", {
      method: "POST",
      body: JSON.stringify({ title: "Engineer" }),
    });

    expect(response.status).toBe(200);
    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(fetchMock.mock.calls[2][1].body).toBe(
      JSON.stringify({ title: "Engineer" }),
    );
  });

  it("passes a successful response straight through", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ ok: true }));
    vi.stubGlobal("fetch", fetchMock);
    const session = await loadSession();

    await session.authFetch("/api/resumes");

    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});

describe("logout", () => {
  it("clears the in-memory token even if the request fails", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ access_token: TOKEN }))
      .mockRejectedValueOnce(new Error("offline"));
    vi.stubGlobal("fetch", fetchMock);
    const session = await loadSession();
    await session.refreshSession();
    expect(session.getAccessToken()).toBe(TOKEN);

    await session.logout();

    expect(session.getAccessToken()).toBeNull();
  });
});

describe("browser storage", () => {
  it("never writes the access token to localStorage or sessionStorage", async () => {
    const localSet = vi.spyOn(window.localStorage, "setItem");
    const sessionSet = vi.spyOn(window.sessionStorage, "setItem");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse({ access_token: TOKEN })),
    );
    const session = await loadSession();

    await session.login("member@example.com", "a password");
    await session.refreshSession();
    await session.authFetch("/api/resumes");

    expect(localSet).not.toHaveBeenCalled();
    expect(sessionSet).not.toHaveBeenCalled();
    expect(JSON.stringify(window.localStorage)).not.toContain(TOKEN);
    expect(JSON.stringify(window.sessionStorage)).not.toContain(TOKEN);
    expect(document.cookie).not.toContain(TOKEN);
  });
});
