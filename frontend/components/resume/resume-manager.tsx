"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { ResumeUpload } from "@/components/resume/resume-upload";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  PARSE_STATUS_LABELS,
  deleteResume,
  fileTypeLabel,
  formatBytes,
  listResumes,
  parseResume,
  type ParseStatus,
  type Resume,
} from "@/lib/api/resumes";
import { useAuth } from "@/lib/auth/context";

const STATUS_VARIANTS: Record<
  ParseStatus,
  "default" | "outline" | "destructive"
> = {
  pending: "outline",
  parsed: "default",
  failed: "destructive",
};

export function ResumeManager() {
  const { status: authStatus } = useAuth();
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [parseError, setParseError] = useState<string | null>(null);
  const [parsingId, setParsingId] = useState<string | null>(null);
  const [pendingDelete, setPendingDelete] = useState<Resume | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [announcement, setAnnouncement] = useState("");
  const [sessionEnded, setSessionEnded] = useState(false);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    if (authStatus === "unauthenticated" || sessionEnded) {
      router.replace("/login");
    }
  }, [authStatus, sessionEnded, router]);

  useEffect(() => {
    if (authStatus !== "authenticated") {
      return;
    }

    let active = true;
    void listResumes().then((result) => {
      if (!active) {
        return;
      }
      setLoading(false);
      if (!result.ok) {
        if (result.unauthorized) {
          setSessionEnded(true);
        } else {
          setLoadError(result.error);
        }
        return;
      }
      setResumes(result.data);
    });

    return () => {
      active = false;
    };
  }, [authStatus, attempt]);

  function retry() {
    setLoading(true);
    setLoadError(null);
    setAttempt((count) => count + 1);
  }

  function added(resume: Resume) {
    setResumes((current) => [resume, ...current]);
    setAnnouncement(`${resume.original_filename} uploaded.`);
  }

  async function runParse(resume: Resume) {
    setParseError(null);
    setParsingId(resume.id);
    const result = await parseResume(resume.id);
    setParsingId(null);

    if (!result.ok) {
      if (result.unauthorized) {
        setSessionEnded(true);
        return;
      }
      setParseError(result.error);
      return;
    }

    setResumes((current) =>
      current.map((item) => (item.id === result.data.id ? result.data : item)),
    );
    setAnnouncement(
      result.data.parse_status === "parsed"
        ? `${result.data.original_filename} read successfully.`
        : `${result.data.original_filename} could not be read.`,
    );
  }

  async function confirmDelete() {
    const resume = pendingDelete;
    if (!resume) {
      return;
    }

    setPendingDelete(null);
    setDeleteError(null);
    setDeletingId(resume.id);
    const result = await deleteResume(resume.id);
    setDeletingId(null);

    if (!result.ok) {
      if (result.unauthorized) {
        setSessionEnded(true);
        return;
      }
      setDeleteError(result.error);
      return;
    }

    setResumes((current) => current.filter((item) => item.id !== resume.id));
    setAnnouncement(`${resume.original_filename} deleted.`);
  }

  return (
    <div className="w-full max-w-[720px] space-y-6">
      <h1 className="font-heading text-xl font-semibold">My resumes</h1>

      <ResumeUpload
        inputRef={fileInputRef}
        onUploaded={added}
        onSessionExpired={() => setSessionEnded(true)}
      />

      <Card>
        <CardHeader>
          <CardTitle>Uploaded resumes</CardTitle>
          <CardDescription>
            Every resume here belongs to your account only.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {authStatus === "loading" || (loading && !loadError) ? (
            <div className="space-y-3" aria-busy="true">
              {[0, 1].map((row) => (
                <div
                  key={row}
                  className="bg-muted h-16 w-full animate-pulse rounded-md"
                />
              ))}
            </div>
          ) : loadError ? (
            <div className="space-y-3">
              <p role="alert" className="text-destructive text-sm">
                {loadError}
              </p>
              <Button variant="secondary" onClick={retry}>
                Try again
              </Button>
            </div>
          ) : resumes.length === 0 ? (
            <div className="flex flex-col items-center gap-3 py-12 text-center">
              <p className="font-heading text-base font-semibold">
                No resumes yet
              </p>
              <p className="text-muted-foreground max-w-[42ch] text-sm">
                Upload a resume to get your career profile, match scores, and
                improvement suggestions.
              </p>
              <Button onClick={() => fileInputRef.current?.click()}>
                Choose a resume file
              </Button>
            </div>
          ) : (
            <ul className="divide-y">
              {resumes.map((resume) => (
                <li
                  key={resume.id}
                  aria-busy={
                    deletingId === resume.id || parsingId === resume.id
                  }
                  className="flex items-start justify-between gap-4 py-3 first:pt-0 last:pb-0"
                >
                  <div className="min-w-0 space-y-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <p className="truncate text-sm font-medium">
                        {resume.original_filename}
                      </p>
                      <Badge variant={STATUS_VARIANTS[resume.parse_status]}>
                        {PARSE_STATUS_LABELS[resume.parse_status]}
                      </Badge>
                    </div>
                    <p className="text-muted-foreground text-xs">
                      {fileTypeLabel(resume.content_type)} ·{" "}
                      {formatBytes(resume.byte_size)} · Uploaded{" "}
                      {new Date(resume.created_at).toLocaleDateString()}
                    </p>
                    {resume.parse_status === "failed" && resume.parse_error && (
                      <p className="text-destructive text-xs">
                        {resume.parse_error}
                      </p>
                    )}
                  </div>
                  <div className="flex shrink-0 items-center gap-2">
                    <Button variant="outline" size="sm" asChild>
                      <Link href={`/resumes/${resume.id}`}>View sections</Link>
                    </Button>
                    {resume.parse_status !== "parsed" && (
                      <Button
                        variant="secondary"
                        size="sm"
                        disabled={parsingId === resume.id}
                        onClick={() => runParse(resume)}
                      >
                        {parsingId === resume.id
                          ? "Reading…"
                          : resume.parse_status === "failed"
                            ? "Try again"
                            : "Read resume"}
                      </Button>
                    )}
                    <Button
                      variant="destructive"
                      size="sm"
                      disabled={deletingId === resume.id}
                      onClick={() => setPendingDelete(resume)}
                    >
                      {deletingId === resume.id ? "Deleting…" : "Delete"}
                    </Button>
                  </div>
                </li>
              ))}
            </ul>
          )}

          {(deleteError ?? parseError) && (
            <p role="alert" className="text-destructive text-sm">
              {deleteError ?? parseError}
            </p>
          )}
        </CardContent>
      </Card>

      <p aria-live="polite" className="sr-only">
        {announcement}
      </p>

      <AlertDialog
        open={pendingDelete !== null}
        onOpenChange={(open) => {
          if (!open) {
            setPendingDelete(null);
          }
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              Delete resume {pendingDelete?.original_filename}?
            </AlertDialogTitle>
            <AlertDialogDescription>
              This permanently deletes the file and cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Keep resume</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDelete}>
              Delete permanently
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
