import { request, type ApiResult } from "@/lib/api/request";

export type ParseStatus = "pending" | "parsed" | "failed";

export type Resume = {
  id: string;
  original_filename: string;
  content_type: string;
  byte_size: number;
  parse_status: ParseStatus;
  parse_error: string | null;
  created_at: string;
  updated_at: string;
};

export const PDF_CONTENT_TYPE = "application/pdf";
export const DOCX_CONTENT_TYPE =
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document";

export const MAX_RESUME_BYTES = 10 * 1024 * 1024;

const LIST_FAILED_MESSAGE =
  "We could not load your resumes. The CareerIQ API may not be running.";
const UPLOAD_FAILED_MESSAGE =
  "We could not upload your resume. Your file is still selected — try again.";
const DELETE_FAILED_MESSAGE =
  "We could not delete this resume. It is still here — try again.";
const PARSE_FAILED_MESSAGE =
  "We could not read this resume just now. Your resume is safe — try again.";

export function listResumes(): Promise<ApiResult<Resume[]>> {
  return request<Resume[]>(
    "/api/resumes",
    { cache: "no-store" },
    LIST_FAILED_MESSAGE,
  );
}

export function uploadResume(file: File): Promise<ApiResult<Resume>> {
  const body = new FormData();
  body.append("file", file);
  return request<Resume>(
    "/api/resumes",
    { method: "POST", body },
    UPLOAD_FAILED_MESSAGE,
  );
}

export function parseResume(id: string): Promise<ApiResult<Resume>> {
  return request<Resume>(
    `/api/resumes/${id}/parse`,
    { method: "POST" },
    PARSE_FAILED_MESSAGE,
  );
}

export function deleteResume(id: string): Promise<ApiResult<void>> {
  return request<void>(
    `/api/resumes/${id}`,
    { method: "DELETE" },
    DELETE_FAILED_MESSAGE,
  );
}

export function fileTypeLabel(contentType: string): string {
  return contentType === PDF_CONTENT_TYPE ? "PDF" : "DOCX";
}

export const PARSE_STATUS_LABELS: Record<ParseStatus, string> = {
  pending: "Not read yet",
  parsed: "Text extracted",
  failed: "Couldn't read",
};

export function formatBytes(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${Math.round(bytes / 1024)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
