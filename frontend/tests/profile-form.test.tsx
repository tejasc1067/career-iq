import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ProfileForm } from "@/components/profile/profile-form";
import { AuthProvider } from "@/lib/auth/context";

const replace = vi.fn();
const routerStub = { push: vi.fn(), replace };
vi.mock("next/navigation", () => ({
  useRouter: () => routerStub,
}));

const TOKEN = "access-token-one";
const SAVED_PROFILE = {
  current_role: "Software Engineer",
  career_level: "Mid-level",
  years_of_experience: 4.5,
  updated_at: "2026-08-21T10:00:00Z",
};
const EMPTY_PROFILE = {
  current_role: null,
  career_level: null,
  years_of_experience: null,
  updated_at: null,
};

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function currentUser(profile: unknown) {
  return {
    id: "11111111-1111-1111-1111-111111111111",
    email: "member@example.com",
    created_at: "2026-08-01T10:00:00Z",
    updated_at: "2026-08-01T10:00:00Z",
    profile,
  };
}

type Handler = (url: string, init?: RequestInit) => Response;

function stubFetch(handler: Handler) {
  const mock = vi.fn((input: RequestInfo | URL, init?: RequestInit) =>
    Promise.resolve(handler(String(input), init)),
  );
  vi.stubGlobal("fetch", mock);
  return mock;
}

function signedInWith(profile: unknown, onSave?: Handler): Handler {
  return (url, init) => {
    if (url.endsWith("/api/auth/refresh")) {
      return json({ access_token: TOKEN });
    }
    if (url.endsWith("/api/users/me")) {
      return json(currentUser(profile));
    }
    if (url.endsWith("/api/users/me/profile")) {
      return onSave
        ? onSave(url, init)
        : json({ ...(init?.body ? JSON.parse(String(init.body)) : {}) });
    }
    return json({ detail: "unexpected" }, 404);
  };
}

function renderForm() {
  return render(
    <AuthProvider>
      <ProfileForm />
    </AuthProvider>,
  );
}

function bodyOf(mock: ReturnType<typeof stubFetch>, path: string) {
  const call = mock.mock.calls.find(([input]) => String(input).endsWith(path));
  return call ? JSON.parse(String((call[1] as RequestInit).body)) : null;
}

beforeEach(() => {
  replace.mockClear();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("profile form", () => {
  it("shows the profile the API returns for the signed-in user", async () => {
    stubFetch(signedInWith(SAVED_PROFILE));
    renderForm();

    expect(
      await screen.findByDisplayValue("Software Engineer"),
    ).toBeInTheDocument();
    expect(screen.getByDisplayValue("Mid-level")).toBeInTheDocument();
    expect(screen.getByDisplayValue("4.5")).toBeInTheDocument();
    expect(screen.getByText(/Signed in as member@example.com/)).toBeVisible();
  });

  it("reports that nothing is saved yet for a new account", async () => {
    stubFetch(signedInWith(EMPTY_PROFILE));
    renderForm();

    expect(await screen.findByText("Not saved yet")).toBeInTheDocument();
    expect(screen.getByLabelText(/Current role/)).toHaveValue("");
  });

  it("saves the edited profile and never sends a user id", async () => {
    const fetchMock = stubFetch(
      signedInWith(EMPTY_PROFILE, () =>
        json({
          current_role: "Java Developer",
          career_level: null,
          years_of_experience: 4.5,
          updated_at: "2026-08-21T12:30:00Z",
        }),
      ),
    );
    renderForm();
    await screen.findByText("Not saved yet");

    fireEvent.change(screen.getByLabelText(/Current role/), {
      target: { value: "Java Developer" },
    });
    fireEvent.change(screen.getByLabelText(/Years of experience/), {
      target: { value: "4.5" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save profile" }));

    expect(await screen.findByText(/Last saved/)).toBeInTheDocument();
    expect(bodyOf(fetchMock, "/api/users/me/profile")).toEqual({
      current_role: "Java Developer",
      career_level: null,
      years_of_experience: 4.5,
    });
  });

  it("rejects an out-of-range experience value without calling the API", async () => {
    const fetchMock = stubFetch(signedInWith(EMPTY_PROFILE));
    renderForm();
    await screen.findByText("Not saved yet");

    fireEvent.change(screen.getByLabelText(/Years of experience/), {
      target: { value: "120" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save profile" }));

    expect(
      await screen.findByText("Enter a value between 0 and 70."),
    ).toBeInTheDocument();
    expect(screen.getByRole("alert")).toHaveTextContent(
      "Your profile was not saved",
    );
    expect(
      fetchMock.mock.calls.filter(([input]) =>
        String(input).endsWith("/api/users/me/profile"),
      ),
    ).toHaveLength(0);
  });

  it("clears a field error once the value is corrected", async () => {
    stubFetch(signedInWith(EMPTY_PROFILE));
    renderForm();
    await screen.findByText("Not saved yet");

    const years = screen.getByLabelText(/Years of experience/);
    fireEvent.change(years, { target: { value: "-3" } });
    fireEvent.blur(years);
    expect(
      await screen.findByText("Enter a value between 0 and 70."),
    ).toBeInTheDocument();

    fireEvent.change(years, { target: { value: "3" } });

    await waitFor(() =>
      expect(
        screen.queryByText("Enter a value between 0 and 70."),
      ).not.toBeInTheDocument(),
    );
  });

  it("keeps the entered values when the save fails", async () => {
    stubFetch(
      signedInWith(EMPTY_PROFILE, () => json({ detail: "boom" }, 500)),
    );
    renderForm();
    await screen.findByText("Not saved yet");

    fireEvent.change(screen.getByLabelText(/Current role/), {
      target: { value: "Java Developer" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save profile" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "We could not save your profile",
    );
    expect(screen.getByLabelText(/Current role/)).toHaveValue("Java Developer");
  });

  it("offers a retry when the profile cannot be loaded", async () => {
    let attempts = 0;
    stubFetch((url) => {
      if (url.endsWith("/api/auth/refresh")) {
        return json({ access_token: TOKEN });
      }
      attempts += 1;
      return attempts === 1
        ? json({ detail: "down" }, 500)
        : json(currentUser(SAVED_PROFILE));
    });
    renderForm();

    fireEvent.click(await screen.findByRole("button", { name: "Try again" }));

    expect(
      await screen.findByDisplayValue("Software Engineer"),
    ).toBeInTheDocument();
  });

  it("sends an unauthenticated visitor to the sign-in page", async () => {
    stubFetch((url) =>
      url.endsWith("/api/auth/refresh")
        ? json({ detail: "no session" }, 401)
        : json({ detail: "unexpected" }, 404),
    );
    renderForm();

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
  });

  it("sends the user to sign in when the session expires mid-session", async () => {
    stubFetch((url) => {
      if (url.endsWith("/api/auth/refresh")) {
        return json({ access_token: TOKEN });
      }
      return json({ detail: "expired" }, 401);
    });
    renderForm();

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
  });
});
