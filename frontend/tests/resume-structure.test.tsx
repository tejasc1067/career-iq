import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ResumeStructure } from "@/components/resume/resume-structure";
import { AuthProvider } from "@/lib/auth/context";

const replace = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace }),
}));

const TOKEN = "access-token-one";
const RESUME_ID = "11111111-1111-1111-1111-111111111111";

const RESUME = {
  id: RESUME_ID,
  original_filename: "backend-engineer.pdf",
  content_type: "application/pdf",
  byte_size: 245_760,
  parse_status: "parsed",
  parse_error: null,
  created_at: "2026-08-20T10:00:00Z",
  updated_at: "2026-08-20T10:00:00Z",
};
const UNREADABLE_RESUME = {
  ...RESUME,
  parse_status: "failed",
  parse_error: "We couldn't read this PDF. Try uploading another PDF.",
};
const SECTIONS = [
  {
    id: "aaaaaaaa-0000-0000-0000-000000000001",
    kind: "other",
    heading: null,
    content: "Jane Doe\njane@example.com",
    position: 0,
  },
  {
    id: "aaaaaaaa-0000-0000-0000-000000000002",
    kind: "summary",
    heading: "PROFESSIONAL SUMMARY",
    content: "Senior data engineer with eight years building pipelines.",
    position: 1,
  },
  {
    id: "aaaaaaaa-0000-0000-0000-000000000003",
    kind: "certifications",
    heading: "CERTIFICATIONS",
    content: "",
    position: 2,
  },
];

type Handler = (url: string, init?: RequestInit) => Response;

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function routes({
  resume = () => json(RESUME),
  sections = () => json([]),
  parse,
}: {
  resume?: Handler;
  sections?: Handler;
  parse?: Handler;
} = {}): Handler {
  return (url, init) => {
    if (url.endsWith("/api/auth/refresh")) {
      return json({ access_token: TOKEN });
    }
    if (url.endsWith("/parse")) {
      return parse ? parse(url, init) : json(RESUME);
    }
    if (url.endsWith("/sections")) {
      return sections(url, init);
    }
    if (url.endsWith(`/api/resumes/${RESUME_ID}`)) {
      return resume(url, init);
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

function renderStructure() {
  return render(
    <AuthProvider>
      <ResumeStructure resumeId={RESUME_ID} />
    </AuthProvider>,
  );
}

beforeEach(() => {
  replace.mockClear();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("resume structure page", () => {
  it("shows a loading state while the resume is fetched", () => {
    stubFetch(routes());
    renderStructure();

    expect(document.querySelector('[aria-busy="true"]')).not.toBeNull();
  });

  it("lists the detected sections in order with their headings", async () => {
    stubFetch(routes({ sections: () => json(SECTIONS) }));
    renderStructure();

    expect(await screen.findByText("Summary")).toBeInTheDocument();
    expect(screen.getByText("PROFESSIONAL SUMMARY")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Senior data engineer with eight years building pipelines.",
      ),
    ).toBeInTheDocument();

    const labels = screen
      .getAllByText(/^(Other|Summary|Certifications)$/)
      .map((node) => node.textContent);
    expect(labels).toEqual(["Other", "Summary", "Certifications"]);
  });

  it("says so when a detected section has no content", async () => {
    stubFetch(routes({ sections: () => json(SECTIONS) }));
    renderStructure();

    expect(
      await screen.findByText("This section is empty in your resume."),
    ).toBeInTheDocument();
  });

  it("shows the resume name and its parse status", async () => {
    stubFetch(routes({ sections: () => json(SECTIONS) }));
    renderStructure();

    expect(
      await screen.findByRole("heading", { name: "backend-engineer.pdf" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Text extracted")).toBeInTheDocument();
  });

  it("offers detection when no sections exist yet", async () => {
    stubFetch(routes());
    renderStructure();

    expect(
      await screen.findByText("No sections detected yet"),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Detect sections" }),
    ).toBeInTheDocument();
  });

  it("detects sections on request and renders them", async () => {
    let detected = false;
    const fetchMock = stubFetch(
      routes({
        sections: () => json(detected ? SECTIONS : []),
        parse: () => {
          detected = true;
          return json(RESUME);
        },
      }),
    );
    renderStructure();
    await screen.findByText("No sections detected yet");

    fireEvent.click(screen.getByRole("button", { name: "Detect sections" }));

    expect(await screen.findByText("Summary")).toBeInTheDocument();
    const parsed = fetchMock.mock.calls.find(([url]) =>
      String(url).endsWith("/parse"),
    );
    expect((parsed?.[1] as RequestInit).method).toBe("POST");
  });

  it("does not request detection on its own", async () => {
    const fetchMock = stubFetch(routes({ sections: () => json(SECTIONS) }));
    renderStructure();
    await screen.findByText("Summary");

    expect(
      fetchMock.mock.calls.some(([url]) => String(url).endsWith("/parse")),
    ).toBe(false);
  });

  it("explains an unreadable resume and offers a retry instead of sections", async () => {
    stubFetch(routes({ resume: () => json(UNREADABLE_RESUME) }));
    renderStructure();

    expect(
      await screen.findByText(
        "We couldn't read this PDF. Try uploading another PDF.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Try again" }),
    ).toBeInTheDocument();
    expect(
      screen.queryByText("No sections detected yet"),
    ).not.toBeInTheDocument();
  });

  it("reports a failed detection without losing the page", async () => {
    stubFetch(
      routes({
        parse: () => json({ detail: "boom" }, 500),
      }),
    );
    renderStructure();
    await screen.findByText("No sections detected yet");

    fireEvent.click(screen.getByRole("button", { name: "Detect sections" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "We could not read this resume just now.",
    );
    expect(screen.getByText("No sections detected yet")).toBeInTheDocument();
  });

  it("offers a retry when the sections cannot be loaded", async () => {
    let attempts = 0;
    stubFetch(
      routes({
        sections: () => {
          attempts += 1;
          return attempts === 1
            ? json({ detail: "boom" }, 500)
            : json(SECTIONS);
        },
      }),
    );
    renderStructure();

    fireEvent.click(await screen.findByRole("button", { name: "Try again" }));

    expect(await screen.findByText("Summary")).toBeInTheDocument();
  });

  it("reports a resume that cannot be found", async () => {
    stubFetch(routes({ resume: () => json({ detail: "not found" }, 404) }));
    renderStructure();

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "We could not find this resume.",
    );
    expect(
      screen.queryByRole("button", { name: "Try again" }),
    ).not.toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: "Back to my resumes" }),
    ).toHaveAttribute("href", "/resumes");
  });

  it("redirects to the login page when the session has expired", async () => {
    stubFetch(routes({ resume: () => json({ detail: "expired" }, 401) }));
    renderStructure();

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
  });

  it("redirects to the login page when the session expires during detection", async () => {
    stubFetch(routes({ parse: () => json({ detail: "expired" }, 401) }));
    renderStructure();
    await screen.findByText("No sections detected yet");

    fireEvent.click(screen.getByRole("button", { name: "Detect sections" }));

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
  });

  it("links back to the resume list", async () => {
    stubFetch(routes({ sections: () => json(SECTIONS) }));
    renderStructure();

    expect(
      await screen.findByRole("link", { name: "← My resumes" }),
    ).toHaveAttribute("href", "/resumes");
  });
});
