import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ResumeManager } from "@/components/resume/resume-manager";
import { AuthProvider } from "@/lib/auth/context";

const replace = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace }),
}));

const TOKEN = "access-token-one";
const PDF_TYPE = "application/pdf";
const DOCX_TYPE =
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document";

const EXISTING = {
  id: "11111111-1111-1111-1111-111111111111",
  original_filename: "backend-engineer.pdf",
  content_type: PDF_TYPE,
  byte_size: 245_760,
  parse_status: "parsed",
  parse_error: null,
  created_at: "2026-08-20T10:00:00Z",
  updated_at: "2026-08-20T10:00:00Z",
};
const UNPARSED = {
  ...EXISTING,
  id: "44444444-4444-4444-4444-444444444444",
  original_filename: "older-upload.pdf",
  parse_status: "pending",
};
const UNREADABLE = {
  ...EXISTING,
  id: "55555555-5555-5555-5555-555555555555",
  original_filename: "scanned.pdf",
  parse_status: "failed",
  parse_error:
    "We couldn't find any text in this PDF. If it is a scan or an image, upload a text-based PDF or a DOCX version instead.",
};
const OTHER = {
  id: "22222222-2222-2222-2222-222222222222",
  original_filename: "data-analyst.docx",
  content_type: DOCX_TYPE,
  byte_size: 51_200,
  parse_status: "parsed",
  parse_error: null,
  created_at: "2026-08-19T10:00:00Z",
  updated_at: "2026-08-19T10:00:00Z",
};
const UPLOADED = {
  id: "33333333-3333-3333-3333-333333333333",
  original_filename: "resume.pdf",
  content_type: PDF_TYPE,
  byte_size: 1024,
  parse_status: "parsed",
  parse_error: null,
  created_at: "2026-08-23T10:00:00Z",
  updated_at: "2026-08-23T10:00:00Z",
};

type Handler = (url: string, init?: RequestInit) => Response;

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function noContent(): Response {
  return new Response(null, { status: 204 });
}

function routes({
  list = () => json([]),
  upload,
  remove,
  parse,
}: {
  list?: Handler;
  upload?: Handler;
  remove?: Handler;
  parse?: Handler;
} = {}): Handler {
  return (url, init) => {
    if (url.endsWith("/api/auth/refresh")) {
      return json({ access_token: TOKEN });
    }
    if (url.endsWith("/api/resumes")) {
      if (init?.method === "POST") {
        return upload ? upload(url, init) : json(UPLOADED, 201);
      }
      return list(url, init);
    }
    if (url.endsWith("/parse")) {
      return parse
        ? parse(url, init)
        : json({ ...UNPARSED, parse_status: "parsed" });
    }
    if (url.includes("/api/resumes/")) {
      return remove ? remove(url, init) : noContent();
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

function fileOfSize(name: string, size: number, type: string): File {
  const file = new File(["x"], name, { type });
  Object.defineProperty(file, "size", { value: size });
  return file;
}

function fileInput(): HTMLInputElement {
  return screen.getByLabelText(
    /drag and drop your resume/i,
  ) as HTMLInputElement;
}

function select(file: File) {
  const input = fileInput();
  Object.defineProperty(input, "files", { value: [file], configurable: true });
  fireEvent.change(input);
}

function uploadButton() {
  return screen.getByRole("button", { name: "Upload resume" });
}

beforeEach(() => {
  replace.mockClear();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("resume page", () => {
  it("shows a loading state while the resumes are fetched", () => {
    stubFetch(routes());
    renderManager();

    expect(document.querySelector('[aria-busy="true"]')).not.toBeNull();
  });

  it("shows the empty state when nothing has been uploaded", async () => {
    stubFetch(routes());
    renderManager();

    expect(await screen.findByText("No resumes yet")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Choose a resume file" }),
    ).toBeInTheDocument();
  });

  it("lists uploaded resumes with type, size and date", async () => {
    stubFetch(routes({ list: () => json([EXISTING, OTHER]) }));
    renderManager();

    const first = (await screen.findByText("backend-engineer.pdf")).closest(
      "li",
    );
    expect(first).toHaveTextContent("PDF");
    expect(first).toHaveTextContent("240 KB");
    expect(first).toHaveTextContent("Uploaded");
    expect(
      screen.getByText("data-analyst.docx").closest("li"),
    ).toHaveTextContent("DOCX");
  });

  it("offers a retry when the resumes cannot be loaded", async () => {
    let attempts = 0;
    stubFetch(
      routes({
        list: () => {
          attempts += 1;
          return attempts === 1
            ? json({ detail: "boom" }, 500)
            : json([EXISTING]);
        },
      }),
    );
    renderManager();

    fireEvent.click(await screen.findByRole("button", { name: "Try again" }));

    expect(await screen.findByText("backend-engineer.pdf")).toBeInTheDocument();
  });

  it("redirects to the login page when the session has expired", async () => {
    stubFetch(routes({ list: () => json({ detail: "expired" }, 401) }));
    renderManager();

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
  });
});

describe("resume selection", () => {
  it("shows the selected filename and size", async () => {
    stubFetch(routes());
    renderManager();
    await screen.findByText("No resumes yet");

    select(fileOfSize("resume.pdf", 2048, PDF_TYPE));

    expect(screen.getByText("resume.pdf")).toBeInTheDocument();
    expect(screen.getByText("2 KB")).toBeInTheDocument();
  });

  it("accepts a file dropped onto the upload area", async () => {
    stubFetch(routes());
    renderManager();
    await screen.findByText("No resumes yet");

    fireEvent.drop(screen.getByText(/drag and drop your resume/i), {
      dataTransfer: { files: [fileOfSize("dropped.pdf", 4096, PDF_TYPE)] },
    });

    expect(screen.getByText("dropped.pdf")).toBeInTheDocument();
  });

  it("removes the selected file", async () => {
    stubFetch(routes());
    renderManager();
    await screen.findByText("No resumes yet");
    select(fileOfSize("resume.pdf", 2048, PDF_TYPE));

    fireEvent.click(screen.getByRole("button", { name: "Remove" }));

    expect(screen.queryByText("resume.pdf")).not.toBeInTheDocument();
  });

  it.each([
    ["an unsupported type", "resume.txt", 2048, "Upload a PDF or DOCX resume."],
    [
      "an empty file",
      "resume.pdf",
      0,
      "This file is empty. Choose your resume file and try again.",
    ],
    [
      "an oversized file",
      "resume.pdf",
      11 * 1024 * 1024,
      "Resumes must be 10 MB or smaller.",
    ],
  ])(
    "rejects %s without calling the API",
    async (_case, name, size, message) => {
      const fetchMock = stubFetch(routes());
      renderManager();
      await screen.findByText("No resumes yet");
      const before = fetchMock.mock.calls.length;

      select(fileOfSize(name, size, PDF_TYPE));

      expect(await screen.findByRole("alert")).toHaveTextContent(message);
      expect(fileInput()).toHaveAttribute("aria-invalid", "true");
      expect(uploadButton()).toBeDisabled();
      expect(fetchMock.mock.calls.length).toBe(before);
    },
  );
});

describe("resume upload", () => {
  it("posts the file as form data and shows it in the list", async () => {
    const fetchMock = stubFetch(routes());
    renderManager();
    await screen.findByText("No resumes yet");
    select(fileOfSize("resume.pdf", 1024, PDF_TYPE));

    fireEvent.click(uploadButton());

    expect(
      await screen.findByRole("button", { name: "Delete" }),
    ).toBeInTheDocument();
    expect(screen.queryByText("No resumes yet")).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Remove" }),
    ).not.toBeInTheDocument();

    const post = fetchMock.mock.calls.find(
      ([url, init]) =>
        String(url).endsWith("/api/resumes") &&
        (init as RequestInit | undefined)?.method === "POST",
    );
    const body = (post?.[1] as RequestInit).body as FormData;
    expect(body).toBeInstanceOf(FormData);
    expect((body.get("file") as File).name).toBe("resume.pdf");
  });

  it("keeps the file and allows a retry after a failed upload", async () => {
    let attempts = 0;
    stubFetch(
      routes({
        upload: () => {
          attempts += 1;
          return attempts === 1
            ? json({ detail: "boom" }, 500)
            : json(UPLOADED, 201);
        },
      }),
    );
    renderManager();
    await screen.findByText("No resumes yet");
    select(fileOfSize("resume.pdf", 1024, PDF_TYPE));

    fireEvent.click(uploadButton());

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "We could not upload your resume.",
    );
    expect(screen.getByText("resume.pdf")).toBeInTheDocument();

    fireEvent.click(uploadButton());

    await waitFor(() =>
      expect(screen.queryByText("No resumes yet")).not.toBeInTheDocument(),
    );
    expect(screen.getByRole("button", { name: "Delete" })).toBeInTheDocument();
  });

  it("marks the form busy while the upload is in flight", async () => {
    let release = () => {};
    const pending = new Promise<void>((resolve) => {
      release = resolve;
    });
    const handler = routes();
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        if (init?.method === "POST" && String(input).endsWith("/api/resumes")) {
          await pending;
        }
        return handler(String(input), init);
      }),
    );
    renderManager();
    await screen.findByText("No resumes yet");
    select(fileOfSize("resume.pdf", 1024, PDF_TYPE));

    fireEvent.click(uploadButton());

    const form = document.querySelector("form");
    await waitFor(() => expect(form).toHaveAttribute("aria-busy", "true"));
    expect(screen.getByRole("button", { name: "Uploading…" })).toBeDisabled();

    release();
    await waitFor(() => expect(form).toHaveAttribute("aria-busy", "false"));
  });

  it("redirects to the login page when the session expired during upload", async () => {
    stubFetch(routes({ upload: () => json({ detail: "expired" }, 401) }));
    renderManager();
    await screen.findByText("No resumes yet");
    select(fileOfSize("resume.pdf", 1024, PDF_TYPE));

    fireEvent.click(uploadButton());

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
  });
});

describe("resume deletion", () => {
  async function openConfirmation() {
    renderManager();
    await screen.findByText("backend-engineer.pdf");
    fireEvent.click(screen.getAllByRole("button", { name: "Delete" })[0]);
    return screen.findByRole("alertdialog");
  }

  it("asks for confirmation naming the resume and warning it is permanent", async () => {
    stubFetch(routes({ list: () => json([EXISTING]) }));

    const dialog = await openConfirmation();

    expect(dialog).toHaveTextContent("Delete resume backend-engineer.pdf?");
    expect(dialog).toHaveTextContent("permanently");
    expect(
      within(dialog).getByRole("button", { name: "Keep resume" }),
    ).toBeInTheDocument();
  });

  it("keeps the resume when the confirmation is cancelled", async () => {
    const fetchMock = stubFetch(routes({ list: () => json([EXISTING]) }));

    const dialog = await openConfirmation();
    fireEvent.click(
      within(dialog).getByRole("button", { name: "Keep resume" }),
    );

    await waitFor(() =>
      expect(screen.queryByRole("alertdialog")).not.toBeInTheDocument(),
    );
    expect(screen.getByText("backend-engineer.pdf")).toBeInTheDocument();
    expect(
      fetchMock.mock.calls.some(
        ([, init]) => (init as RequestInit | undefined)?.method === "DELETE",
      ),
    ).toBe(false);
  });

  it("removes the resume once deletion is confirmed", async () => {
    const fetchMock = stubFetch(
      routes({ list: () => json([EXISTING, OTHER]) }),
    );

    const dialog = await openConfirmation();
    fireEvent.click(
      within(dialog).getByRole("button", { name: "Delete permanently" }),
    );

    await waitFor(() =>
      expect(
        screen.queryByText("backend-engineer.pdf"),
      ).not.toBeInTheDocument(),
    );
    expect(screen.getByText("data-analyst.docx")).toBeInTheDocument();
    const deleted = fetchMock.mock.calls.find(
      ([, init]) => (init as RequestInit | undefined)?.method === "DELETE",
    );
    expect(String(deleted?.[0])).toContain(`/api/resumes/${EXISTING.id}`);
  });

  it("keeps the resume visible when deletion fails", async () => {
    stubFetch(
      routes({
        list: () => json([EXISTING]),
        remove: () => json({ detail: "boom" }, 500),
      }),
    );

    const dialog = await openConfirmation();
    fireEvent.click(
      within(dialog).getByRole("button", { name: "Delete permanently" }),
    );

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "We could not delete this resume.",
    );
    expect(screen.getByText("backend-engineer.pdf")).toBeInTheDocument();
  });

  it("redirects to the login page when the session expired during deletion", async () => {
    stubFetch(
      routes({
        list: () => json([EXISTING]),
        remove: () => json({ detail: "expired" }, 401),
      }),
    );

    const dialog = await openConfirmation();
    fireEvent.click(
      within(dialog).getByRole("button", { name: "Delete permanently" }),
    );

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
  });
});

describe("resume parsing status", () => {
  it("shows the extracted-text status for a parsed resume", async () => {
    stubFetch(routes({ list: () => json([EXISTING]) }));
    renderManager();

    const row = (await screen.findByText("backend-engineer.pdf")).closest("li");
    expect(row).toHaveTextContent("Text extracted");
    expect(
      within(row as HTMLElement).queryByRole("button", { name: "Read resume" }),
    ).not.toBeInTheDocument();
  });

  it("offers to read a resume that was never parsed", async () => {
    stubFetch(routes({ list: () => json([UNPARSED]) }));
    renderManager();

    const row = (await screen.findByText("older-upload.pdf")).closest("li");
    expect(row).toHaveTextContent("Not read yet");
    expect(
      within(row as HTMLElement).getByRole("button", { name: "Read resume" }),
    ).toBeInTheDocument();
  });

  it("shows why a resume could not be read and offers a retry", async () => {
    stubFetch(routes({ list: () => json([UNREADABLE]) }));
    renderManager();

    const row = (await screen.findByText("scanned.pdf")).closest("li");
    expect(row).toHaveTextContent("Couldn't read");
    expect(row).toHaveTextContent("We couldn't find any text in this PDF.");
    expect(
      within(row as HTMLElement).getByRole("button", { name: "Try again" }),
    ).toBeInTheDocument();
  });

  it("does not request parsing until the user asks", async () => {
    const fetchMock = stubFetch(routes({ list: () => json([UNPARSED]) }));
    renderManager();
    await screen.findByText("older-upload.pdf");

    expect(
      fetchMock.mock.calls.some(([url]) => String(url).endsWith("/parse")),
    ).toBe(false);
  });

  it("updates the status after a successful read", async () => {
    const fetchMock = stubFetch(routes({ list: () => json([UNPARSED]) }));
    renderManager();
    await screen.findByText("older-upload.pdf");

    fireEvent.click(screen.getByRole("button", { name: "Read resume" }));

    expect(await screen.findByText("Text extracted")).toBeInTheDocument();
    const parsed = fetchMock.mock.calls.find(([url]) =>
      String(url).endsWith("/parse"),
    );
    expect(String(parsed?.[0])).toContain(`/api/resumes/${UNPARSED.id}/parse`);
    expect((parsed?.[1] as RequestInit).method).toBe("POST");
  });

  it("marks the row busy while the resume is being read", async () => {
    let release = () => {};
    const pending = new Promise<void>((resolve) => {
      release = resolve;
    });
    const handler = routes({ list: () => json([UNPARSED]) });
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        if (String(input).endsWith("/parse")) {
          await pending;
        }
        return handler(String(input), init);
      }),
    );
    renderManager();
    await screen.findByText("older-upload.pdf");

    fireEvent.click(screen.getByRole("button", { name: "Read resume" }));

    const row = screen.getByText("older-upload.pdf").closest("li");
    await waitFor(() => expect(row).toHaveAttribute("aria-busy", "true"));
    expect(screen.getByRole("button", { name: "Reading…" })).toBeDisabled();

    release();
    await waitFor(() => expect(row).toHaveAttribute("aria-busy", "false"));
  });

  it("keeps the resume and reports the reason when reading fails again", async () => {
    stubFetch(
      routes({
        list: () => json([UNPARSED]),
        parse: () =>
          json({
            ...UNPARSED,
            parse_status: "failed",
            parse_error:
              "We couldn't read this PDF. Try uploading another PDF.",
          }),
      }),
    );
    renderManager();
    await screen.findByText("older-upload.pdf");

    fireEvent.click(screen.getByRole("button", { name: "Read resume" }));

    expect(await screen.findByText("Couldn't read")).toBeInTheDocument();
    expect(screen.getByText("older-upload.pdf")).toBeInTheDocument();
    expect(
      screen.getByText("We couldn't read this PDF. Try uploading another PDF."),
    ).toBeInTheDocument();
  });

  it("reports a failed parse request without changing the resume", async () => {
    stubFetch(
      routes({
        list: () => json([UNPARSED]),
        parse: () => json({ detail: "boom" }, 500),
      }),
    );
    renderManager();
    await screen.findByText("older-upload.pdf");

    fireEvent.click(screen.getByRole("button", { name: "Read resume" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "We could not read this resume just now.",
    );
    expect(screen.getByText("older-upload.pdf")).toBeInTheDocument();
    expect(screen.getByText("Not read yet")).toBeInTheDocument();
  });

  it("redirects to the login page when the session expired during a read", async () => {
    stubFetch(
      routes({
        list: () => json([UNPARSED]),
        parse: () => json({ detail: "expired" }, 401),
      }),
    );
    renderManager();
    await screen.findByText("older-upload.pdf");

    fireEvent.click(screen.getByRole("button", { name: "Read resume" }));

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
  });

  it("shows the status of a freshly uploaded resume", async () => {
    stubFetch(routes());
    renderManager();
    await screen.findByText("No resumes yet");
    select(fileOfSize("resume.pdf", 1024, PDF_TYPE));

    fireEvent.click(uploadButton());

    expect(await screen.findByText("Text extracted")).toBeInTheDocument();
  });
});
