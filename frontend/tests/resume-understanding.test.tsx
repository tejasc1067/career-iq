import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ResumeManager } from "@/components/resume/resume-manager";
import { AuthProvider } from "@/lib/auth/context";

const replace = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace }),
}));

const TOKEN = "access-token-one";

const PARSED = {
  id: "11111111-1111-1111-1111-111111111111",
  original_filename: "backend-engineer.pdf",
  content_type: "application/pdf",
  byte_size: 245_760,
  parse_status: "parsed",
  parse_error: null,
  is_understood: false,
  created_at: "2026-08-20T10:00:00Z",
  updated_at: "2026-08-20T10:00:00Z",
};
const UNDERSTOOD_RESUME = { ...PARSED, is_understood: true };
const UNPARSED = { ...PARSED, parse_status: "pending" };

const UNDERSTANDING = {
  contact: {
    full_name: "Jane Doe",
    email: "jane@example.com",
    phone: "+1 555 0100",
    location: "Berlin",
    linkedin_url: null,
    github_url: null,
  },
  professional_summary: "Senior data engineer with eight years of pipelines.",
  experience: [
    {
      company: "Acme Corp",
      role: "Senior Data Engineer",
      location: "Berlin",
      start_date: "2020",
      end_date: null,
      is_current: true,
      highlights: ["Built streaming ingestion for 40 sources."],
    },
  ],
  skills: [
    { name: "Python", category: "Programming" },
    { name: "Airflow", category: null },
  ],
  education: [
    {
      institution: "State University",
      degree: "BSc",
      field_of_study: "Computer Science",
      start_date: "2012",
      end_date: "2016",
    },
  ],
  projects: [
    {
      name: "dbt operator",
      description: "An Airflow operator for dbt runs.",
      technologies: ["Python", "Airflow"],
    },
  ],
  certifications: [
    {
      name: "AWS Certified Data Engineer",
      issuing_organization: "Amazon Web Services",
      date: "2023",
    },
  ],
};

type Handler = (url: string, init?: RequestInit) => Response;

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function routes({
  list = () => json([PARSED]),
  understand,
  understanding,
  remove,
}: {
  list?: Handler;
  understand?: Handler;
  understanding?: Handler;
  remove?: Handler;
} = {}): Handler {
  return (url, init) => {
    if (url.endsWith("/api/auth/refresh")) {
      return json({ access_token: TOKEN });
    }
    if (url.endsWith("/understand")) {
      return understand ? understand(url, init) : json(UNDERSTANDING);
    }
    if (url.endsWith("/understanding")) {
      return understanding ? understanding(url, init) : json(UNDERSTANDING);
    }
    if (url.endsWith("/api/resumes")) {
      return list(url, init);
    }
    if (url.includes("/api/resumes/")) {
      return remove ? remove(url, init) : new Response(null, { status: 204 });
    }
    return json({ detail: "unexpected" }, 404);
  };
}

function stubFetch(handler: Handler) {
  const mock = vi.fn((input: RequestInfo | URL, init?: RequestInit) =>
    Promise.resolve(handler(String(input), init)),
  );
  vi.stubGlobal("fetch", mock);
  return mock;
}

function renderManager() {
  return render(
    <AuthProvider>
      <ResumeManager />
    </AuthProvider>,
  );
}

beforeEach(() => {
  replace.mockClear();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("ai resume understanding", () => {
  it("offers the AI action for a resume whose text has been read", async () => {
    stubFetch(routes());
    renderManager();

    expect(
      await screen.findByRole("button", { name: "Understand with AI" }),
    ).toBeInTheDocument();
  });

  it("does not offer the AI action before the text has been read", async () => {
    stubFetch(routes({ list: () => json([UNPARSED]) }));
    renderManager();

    await screen.findByText("backend-engineer.pdf");
    expect(
      screen.queryByRole("button", { name: "Understand with AI" }),
    ).not.toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Read resume" }),
    ).toBeInTheDocument();
  });

  it("never calls the model without being asked", async () => {
    const fetchMock = stubFetch(routes());
    renderManager();
    await screen.findByRole("button", { name: "Understand with AI" });

    expect(
      fetchMock.mock.calls.some(([url]) => String(url).endsWith("/understand")),
    ).toBe(false);
  });

  it("shows a busy state while the model is reading", async () => {
    let release = () => {};
    const pending = new Promise<void>((resolve) => {
      release = resolve;
    });
    const handler = routes();
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        if (String(input).endsWith("/understand")) {
          await pending;
        }
        return handler(String(input), init);
      }),
    );
    renderManager();

    fireEvent.click(
      await screen.findByRole("button", { name: "Understand with AI" }),
    );

    const row = screen.getByText("backend-engineer.pdf").closest("li");
    await waitFor(() => expect(row).toHaveAttribute("aria-busy", "true"));
    expect(
      screen.getByRole("button", { name: "Understanding…" }),
    ).toBeDisabled();

    release();
    await waitFor(() => expect(row).toHaveAttribute("aria-busy", "false"));
  });

  it("posts to the understand endpoint and shows the structured resume", async () => {
    const fetchMock = stubFetch(routes());
    renderManager();

    fireEvent.click(
      await screen.findByRole("button", { name: "Understand with AI" }),
    );

    expect(await screen.findByText("Jane Doe")).toBeInTheDocument();
    const call = fetchMock.mock.calls.find(([url]) =>
      String(url).endsWith("/understand"),
    );
    expect(String(call?.[0])).toContain(`/api/resumes/${PARSED.id}/understand`);
    expect((call?.[1] as RequestInit).method).toBe("POST");
  });

  it("renders every part of the structured resume", async () => {
    stubFetch(routes());
    renderManager();

    fireEvent.click(
      await screen.findByRole("button", { name: "Understand with AI" }),
    );
    await screen.findByText("Jane Doe");

    expect(
      screen.getByText("jane@example.com · +1 555 0100 · Berlin"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Senior data engineer with eight years of pipelines."),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Senior Data Engineer · Acme Corp"),
    ).toBeInTheDocument();
    expect(screen.getByText("2020 – Present · Berlin")).toBeInTheDocument();
    expect(
      screen.getByText("Built streaming ingestion for 40 sources."),
    ).toBeInTheDocument();
    expect(screen.getByText("Python · Programming")).toBeInTheDocument();
    expect(screen.getByText("Airflow")).toBeInTheDocument();
    expect(screen.getByText("BSc, Computer Science")).toBeInTheDocument();
    expect(screen.getByText("dbt operator")).toBeInTheDocument();
    expect(screen.getByText("AWS Certified Data Engineer")).toBeInTheDocument();
    for (const heading of [
      "Contact",
      "Summary",
      "Experience",
      "Skills",
      "Education",
      "Projects",
      "Certifications",
    ]) {
      expect(
        screen.getByRole("heading", { name: heading }),
      ).toBeInTheDocument();
    }
  });

  it("loads a stored understanding on demand for an understood resume", async () => {
    const fetchMock = stubFetch(
      routes({ list: () => json([UNDERSTOOD_RESUME]) }),
    );
    renderManager();

    fireEvent.click(
      await screen.findByRole("button", { name: "View details" }),
    );

    expect(await screen.findByText("Jane Doe")).toBeInTheDocument();
    expect(
      fetchMock.mock.calls.some(([url]) =>
        String(url).endsWith("/understanding"),
      ),
    ).toBe(true);
    expect(
      fetchMock.mock.calls.some(([url]) => String(url).endsWith("/understand")),
    ).toBe(false);
  });

  it("hides the details again without refetching", async () => {
    const fetchMock = stubFetch(
      routes({ list: () => json([UNDERSTOOD_RESUME]) }),
    );
    renderManager();
    fireEvent.click(
      await screen.findByRole("button", { name: "View details" }),
    );
    await screen.findByText("Jane Doe");
    const before = fetchMock.mock.calls.length;

    fireEvent.click(screen.getByRole("button", { name: "Hide details" }));

    await waitFor(() =>
      expect(screen.queryByText("Jane Doe")).not.toBeInTheDocument(),
    );
    fireEvent.click(screen.getByRole("button", { name: "View details" }));
    await screen.findByText("Jane Doe");
    expect(fetchMock.mock.calls.length).toBe(before);
  });

  it("can run understanding again for an understood resume", async () => {
    const fetchMock = stubFetch(
      routes({ list: () => json([UNDERSTOOD_RESUME]) }),
    );
    renderManager();

    fireEvent.click(
      await screen.findByRole("button", { name: "Understand again" }),
    );

    expect(await screen.findByText("Jane Doe")).toBeInTheDocument();
    expect(
      fetchMock.mock.calls.filter(([url]) =>
        String(url).endsWith("/understand"),
      ).length,
    ).toBe(1);
  });

  it("keeps the resume and reports a safe error when the model fails", async () => {
    stubFetch(
      routes({ understand: () => json({ detail: "model failed" }, 500) }),
    );
    renderManager();

    fireEvent.click(
      await screen.findByRole("button", { name: "Understand with AI" }),
    );

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "We could not understand this resume just now.",
    );
    expect(screen.getByText("backend-engineer.pdf")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Understand with AI" }),
    ).toBeInTheDocument();
    expect(screen.queryByText("Jane Doe")).not.toBeInTheDocument();
  });

  it("allows a retry after a failed understanding", async () => {
    let attempts = 0;
    stubFetch(
      routes({
        understand: () => {
          attempts += 1;
          return attempts === 1
            ? json({ detail: "model failed" }, 500)
            : json(UNDERSTANDING);
        },
      }),
    );
    renderManager();
    fireEvent.click(
      await screen.findByRole("button", { name: "Understand with AI" }),
    );
    await screen.findByRole("alert");

    fireEvent.click(screen.getByRole("button", { name: "Understand with AI" }));

    expect(await screen.findByText("Jane Doe")).toBeInTheDocument();
  });

  it("reports unusable model output without showing anything raw", async () => {
    stubFetch(
      routes({
        understand: () =>
          json({ detail: "We couldn't understand this resume." }, 422),
      }),
    );
    renderManager();

    fireEvent.click(
      await screen.findByRole("button", { name: "Understand with AI" }),
    );

    expect(await screen.findByRole("alert")).toBeInTheDocument();
    expect(screen.getByText("backend-engineer.pdf")).toBeInTheDocument();
  });

  it("redirects to the login page when the session expired", async () => {
    stubFetch(routes({ understand: () => json({ detail: "expired" }, 401) }));
    renderManager();

    fireEvent.click(
      await screen.findByRole("button", { name: "Understand with AI" }),
    );

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
  });

  it("still allows deleting a resume that has been understood", async () => {
    stubFetch(routes({ list: () => json([UNDERSTOOD_RESUME]) }));
    renderManager();
    fireEvent.click(await screen.findByRole("button", { name: "Delete" }));

    const dialog = await screen.findByRole("alertdialog");
    fireEvent.click(screen.getByRole("button", { name: "Delete permanently" }));

    await waitFor(() =>
      expect(
        screen.queryByText("backend-engineer.pdf"),
      ).not.toBeInTheDocument(),
    );
    expect(dialog).not.toBeInTheDocument();
  });
});
