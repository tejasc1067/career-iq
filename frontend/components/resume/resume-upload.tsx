"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  MAX_RESUME_BYTES,
  formatBytes,
  uploadResume,
  type Resume,
} from "@/lib/api/resumes";

const ACCEPTED_EXTENSIONS = [".pdf", ".docx"];
const MAX_MEGABYTES = MAX_RESUME_BYTES / (1024 * 1024);

export const UNSUPPORTED_FORMAT_MESSAGE = "Upload a PDF or DOCX resume.";
export const EMPTY_FILE_MESSAGE =
  "This file is empty. Choose your resume file and try again.";
export const TOO_LARGE_MESSAGE = `Resumes must be ${MAX_MEGABYTES} MB or smaller.`;

function validate(file: File): string | undefined {
  const name = file.name.toLowerCase();
  if (!ACCEPTED_EXTENSIONS.some((extension) => name.endsWith(extension))) {
    return UNSUPPORTED_FORMAT_MESSAGE;
  }
  if (file.size === 0) {
    return EMPTY_FILE_MESSAGE;
  }
  if (file.size > MAX_RESUME_BYTES) {
    return TOO_LARGE_MESSAGE;
  }
  return undefined;
}

export function ResumeUpload({
  inputRef,
  onUploaded,
  onSessionExpired,
}: {
  inputRef: React.RefObject<HTMLInputElement | null>;
  onUploaded: (resume: Resume) => void;
  onSessionExpired: () => void;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [invalid, setInvalid] = useState<string | null>(null);
  const [failure, setFailure] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [dragging, setDragging] = useState(false);

  function select(chosen: File | undefined) {
    if (!chosen) {
      return;
    }
    setStatus(null);
    setFailure(null);
    setFile(chosen);
    setInvalid(validate(chosen) ?? null);
  }

  function clearSelection() {
    setFile(null);
    setInvalid(null);
    setFailure(null);
    if (inputRef.current) {
      inputRef.current.value = "";
    }
  }

  function remove() {
    clearSelection();
    setStatus(null);
  }

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file || invalid) {
      return;
    }

    setFailure(null);
    setUploading(true);
    const result = await uploadResume(file);
    setUploading(false);

    if (!result.ok) {
      if (result.unauthorized) {
        onSessionExpired();
        return;
      }
      setFailure(result.error);
      return;
    }

    clearSelection();
    setStatus(`Uploaded ${result.data.original_filename}.`);
    onUploaded(result.data);
  }

  const message = invalid ?? failure;

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Upload your resume to get started</CardTitle>
        <CardDescription>
          PDF or DOCX, up to {MAX_MEGABYTES} MB. CareerIQ stores your resume and
          reads its text on this machine.
        </CardDescription>
      </CardHeader>

      <form onSubmit={submit} aria-busy={uploading} noValidate>
        <CardContent className="space-y-4">
          <label
            htmlFor="resume-file"
            onDragOver={(event) => {
              event.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={(event) => {
              event.preventDefault();
              setDragging(false);
              select(event.dataTransfer.files[0]);
            }}
            className={`flex cursor-pointer flex-col items-center gap-1 rounded-lg border border-dashed px-4 py-8 text-center transition-colors has-[input:focus-visible]:border-ring has-[input:focus-visible]:ring-3 has-[input:focus-visible]:ring-ring/50 ${
              dragging ? "border-primary bg-accent" : "border-input"
            }`}
          >
            <span className="text-sm font-medium">
              Drag and drop your resume, or browse
            </span>
            <span className="text-muted-foreground text-xs">
              PDF or DOCX only
            </span>
            <input
              ref={inputRef}
              id="resume-file"
              name="file"
              type="file"
              accept={ACCEPTED_EXTENSIONS.join(",")}
              disabled={uploading}
              aria-invalid={Boolean(invalid)}
              aria-describedby="resume-file-message"
              className="sr-only"
              onChange={(event) => select(event.target.files?.[0])}
            />
          </label>

          {file && (
            <div className="flex items-center justify-between gap-4 rounded-md border p-3">
              <div className="min-w-0">
                <p className="truncate text-sm font-medium">{file.name}</p>
                <p className="text-muted-foreground text-xs">
                  {formatBytes(file.size)}
                </p>
              </div>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={remove}
                disabled={uploading}
              >
                Remove
              </Button>
            </div>
          )}

          <p
            id="resume-file-message"
            role={message ? "alert" : undefined}
            className={
              message
                ? "text-destructive text-xs"
                : "text-muted-foreground text-xs"
            }
          >
            {message ??
              "CareerIQ never changes your resume without your approval."}
          </p>
        </CardContent>

        <CardFooter className="mt-6 flex items-center justify-between gap-4">
          <p className="text-muted-foreground text-xs" aria-live="polite">
            {uploading ? "Uploading…" : (status ?? "")}
          </p>
          <Button
            type="submit"
            disabled={uploading || !file || Boolean(invalid)}
          >
            {uploading ? "Uploading…" : "Upload resume"}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
