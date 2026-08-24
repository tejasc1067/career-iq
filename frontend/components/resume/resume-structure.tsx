"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

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
  fetchResume,
  formatBytes,
  listResumeSections,
  parseResume,
  sectionKindLabel,
  type Resume,
  type ResumeSection,
} from "@/lib/api/resumes";
import { useAuth } from "@/lib/auth/context";

export function ResumeStructure({ resumeId }: { resumeId: string }) {
  const { status: authStatus } = useAuth();
  const router = useRouter();

  const [resume, setResume] = useState<Resume | null>(null);
  const [sections, setSections] = useState<ResumeSection[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [detectError, setDetectError] = useState<string | null>(null);
  const [detecting, setDetecting] = useState(false);
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
    void Promise.all([
      fetchResume(resumeId),
      listResumeSections(resumeId),
    ]).then(([resumeResult, sectionsResult]) => {
      if (!active) {
        return;
      }
      setLoading(false);

      if (!resumeResult.ok) {
        if (resumeResult.unauthorized) {
          setSessionEnded(true);
        } else if (resumeResult.notFound) {
          setNotFound(true);
        } else {
          setLoadError(resumeResult.error);
        }
        return;
      }
      setResume(resumeResult.data);

      if (!sectionsResult.ok) {
        if (sectionsResult.unauthorized) {
          setSessionEnded(true);
        } else if (sectionsResult.notFound) {
          setNotFound(true);
        } else {
          setLoadError(sectionsResult.error);
        }
        return;
      }
      setSections(sectionsResult.data);
    });

    return () => {
      active = false;
    };
  }, [authStatus, resumeId, attempt]);

  function retry() {
    setLoading(true);
    setLoadError(null);
    setAttempt((count) => count + 1);
  }

  async function detect() {
    setDetectError(null);
    setDetecting(true);
    const parsed = await parseResume(resumeId);
    if (!parsed.ok) {
      setDetecting(false);
      if (parsed.unauthorized) {
        setSessionEnded(true);
        return;
      }
      setDetectError(parsed.error);
      return;
    }

    const detected = await listResumeSections(resumeId);
    setDetecting(false);
    if (!detected.ok) {
      if (detected.unauthorized) {
        setSessionEnded(true);
        return;
      }
      setDetectError(detected.error);
      return;
    }

    setResume(parsed.data);
    setSections(detected.data);
  }

  if (authStatus === "loading" || (loading && !loadError)) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Resume structure</CardTitle>
          <CardDescription>Loading this resume…</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3" aria-busy="true">
          {[0, 1, 2].map((row) => (
            <div
              key={row}
              className="bg-muted h-20 w-full animate-pulse rounded-md"
            />
          ))}
        </CardContent>
      </Card>
    );
  }

  if (loadError || notFound) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Resume structure</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p role="alert" className="text-destructive text-sm">
            {notFound ? "We could not find this resume." : loadError}
          </p>
          <div className="flex gap-2">
            {loadError && (
              <Button variant="secondary" onClick={retry}>
                Try again
              </Button>
            )}
            <Button variant="outline" asChild>
              <Link href="/resumes">Back to my resumes</Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="w-full space-y-6">
      <div className="space-y-2">
        <Link
          href="/resumes"
          className="text-muted-foreground hover:text-foreground text-sm"
        >
          ← My resumes
        </Link>
        <div className="flex flex-wrap items-center gap-2">
          <h1 className="font-heading text-xl font-semibold">
            {resume?.original_filename}
          </h1>
          {resume && (
            <Badge
              variant={
                resume.parse_status === "parsed"
                  ? "default"
                  : resume.parse_status === "failed"
                    ? "destructive"
                    : "outline"
              }
            >
              {PARSE_STATUS_LABELS[resume.parse_status]}
            </Badge>
          )}
        </div>
        {resume && (
          <p className="text-muted-foreground text-xs">
            {formatBytes(resume.byte_size)} · Uploaded{" "}
            {new Date(resume.created_at).toLocaleDateString()}
          </p>
        )}
      </div>

      <Card aria-busy={detecting}>
        <CardHeader>
          <CardTitle>Detected sections</CardTitle>
          <CardDescription>
            CareerIQ found these sections in your resume. Nothing here is
            invented — every line comes from the file you uploaded.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {resume?.parse_status === "failed" ? (
            <div className="space-y-3">
              <p className="text-sm">
                {resume.parse_error ??
                  "We could not read the text of this resume."}
              </p>
              <Button onClick={detect} disabled={detecting}>
                {detecting ? "Reading…" : "Try again"}
              </Button>
            </div>
          ) : sections.length === 0 ? (
            <div className="flex flex-col items-center gap-3 py-10 text-center">
              <p className="font-heading text-base font-semibold">
                No sections detected yet
              </p>
              <p className="text-muted-foreground max-w-[42ch] text-sm">
                Read this resume again and CareerIQ will identify its summary,
                experience, education, skills and other sections.
              </p>
              <Button onClick={detect} disabled={detecting}>
                {detecting ? "Reading…" : "Detect sections"}
              </Button>
            </div>
          ) : (
            <ol className="space-y-4">
              {sections.map((section) => (
                <li key={section.id} className="space-y-1.5">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant="secondary">
                      {sectionKindLabel(section.kind)}
                    </Badge>
                    {section.heading && (
                      <span className="text-muted-foreground text-xs">
                        {section.heading}
                      </span>
                    )}
                  </div>
                  {section.content ? (
                    <p className="text-sm whitespace-pre-wrap">
                      {section.content}
                    </p>
                  ) : (
                    <p className="text-muted-foreground text-sm italic">
                      This section is empty in your resume.
                    </p>
                  )}
                </li>
              ))}
            </ol>
          )}

          {detectError && (
            <p role="alert" className="text-destructive text-sm">
              {detectError}
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
