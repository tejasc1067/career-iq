"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  fetchCurrentUser,
  saveUserProfile,
  type UserProfile,
  type UserProfileInput,
} from "@/lib/api/users";
import { useAuth } from "@/lib/auth/context";

const CURRENT_ROLE_MAX_LENGTH = 120;
const CAREER_LEVEL_MAX_LENGTH = 80;
const YEARS_MIN = 0;
const YEARS_MAX = 70;

type FieldName = "current_role" | "career_level" | "years_of_experience";
type Values = Record<FieldName, string>;
type Errors = Partial<Record<FieldName, string>>;

const FIELD_LABELS: Record<FieldName, string> = {
  current_role: "Current role",
  career_level: "Career level",
  years_of_experience: "Years of experience",
};

const EMPTY_VALUES: Values = {
  current_role: "",
  career_level: "",
  years_of_experience: "",
};

function toValues(profile: UserProfile): Values {
  return {
    current_role: profile.current_role ?? "",
    career_level: profile.career_level ?? "",
    years_of_experience:
      profile.years_of_experience === null
        ? ""
        : String(profile.years_of_experience),
  };
}

function toPayload(values: Values): UserProfileInput {
  const years = values.years_of_experience.trim();
  return {
    current_role: values.current_role.trim() || null,
    career_level: values.career_level.trim() || null,
    years_of_experience: years === "" ? null : Number(years),
  };
}

function validateField(name: FieldName, value: string): string | undefined {
  const trimmed = value.trim();
  if (trimmed === "") {
    return undefined;
  }

  if (name === "current_role" && trimmed.length > CURRENT_ROLE_MAX_LENGTH) {
    return `Use ${CURRENT_ROLE_MAX_LENGTH} characters or fewer.`;
  }
  if (name === "career_level" && trimmed.length > CAREER_LEVEL_MAX_LENGTH) {
    return `Use ${CAREER_LEVEL_MAX_LENGTH} characters or fewer.`;
  }
  if (name === "years_of_experience") {
    const years = Number(trimmed);
    if (!Number.isFinite(years)) {
      return "Enter a number of years, for example 4.5.";
    }
    if (years < YEARS_MIN || years > YEARS_MAX) {
      return `Enter a value between ${YEARS_MIN} and ${YEARS_MAX}.`;
    }
  }
  return undefined;
}

function validateAll(values: Values): Errors {
  const errors: Errors = {};
  for (const name of Object.keys(values) as FieldName[]) {
    const message = validateField(name, values[name]);
    if (message) {
      errors[name] = message;
    }
  }
  return errors;
}

export function ProfileForm() {
  const { status: authStatus } = useAuth();
  const router = useRouter();
  const summaryRef = useRef<HTMLDivElement>(null);

  const [email, setEmail] = useState<string | null>(null);
  const [values, setValues] = useState<Values>(EMPTY_VALUES);
  const [errors, setErrors] = useState<Errors>({});
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [savedAt, setSavedAt] = useState<string | null>(null);
  const [showSummary, setShowSummary] = useState(false);
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
    void fetchCurrentUser().then((result) => {
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
      setEmail(result.data.email);
      setValues(toValues(result.data.profile));
      setSavedAt(result.data.profile.updated_at);
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

  useEffect(() => {
    if (showSummary) {
      summaryRef.current?.focus();
    }
  }, [showSummary]);

  function change(name: FieldName, value: string) {
    setValues((current) => ({ ...current, [name]: value }));
    if (errors[name]) {
      setErrors((current) => ({
        ...current,
        [name]: validateField(name, value),
      }));
    }
  }

  function blur(name: FieldName) {
    setErrors((current) => ({
      ...current,
      [name]: validateField(name, values[name]),
    }));
  }

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const found = validateAll(values);
    setErrors(found);
    setSaveError(null);

    if (Object.keys(found).length > 0) {
      setShowSummary(true);
      return;
    }
    setShowSummary(false);

    setSaving(true);
    const result = await saveUserProfile(toPayload(values));
    setSaving(false);

    if (!result.ok) {
      if (result.unauthorized) {
        setSessionEnded(true);
        return;
      }
      setSaveError(result.error);
      return;
    }

    setValues(toValues(result.data));
    setSavedAt(result.data.updated_at);
  }

  if (authStatus === "loading" || (loading && !loadError)) {
    return (
      <Card className="w-full max-w-[640px]">
        <CardHeader>
          <CardTitle>My profile</CardTitle>
          <CardDescription>Loading your profile…</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6" aria-busy="true">
          {[0, 1, 2].map((row) => (
            <div key={row} className="space-y-2">
              <div className="bg-muted h-3 w-28 animate-pulse rounded-sm" />
              <div className="bg-muted h-9 w-full animate-pulse rounded-md" />
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  if (loadError) {
    return (
      <Card className="w-full max-w-[640px]">
        <CardHeader>
          <CardTitle>My profile</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p role="alert" className="text-destructive text-sm">
            {loadError}
          </p>
          <Button variant="secondary" onClick={retry}>
            Try again
          </Button>
        </CardContent>
      </Card>
    );
  }

  const failing = (Object.keys(FIELD_LABELS) as FieldName[]).filter(
    (name) => errors[name],
  );

  return (
    <Card className="w-full max-w-[640px]">
      <CardHeader>
        <CardTitle>My profile</CardTitle>
        <CardDescription>
          {email ? `Signed in as ${email}. ` : ""}
          CareerIQ treats what you enter here as authoritative, and never
          invents details you have not provided.
        </CardDescription>
      </CardHeader>

      <form onSubmit={submit} noValidate>
        <CardContent className="space-y-5">
          {showSummary && failing.length > 0 && (
            <div
              ref={summaryRef}
              role="alert"
              tabIndex={-1}
              className="border-destructive/40 bg-destructive/10 text-destructive rounded-md border p-3 text-sm"
            >
              <p className="font-medium">
                Your profile was not saved. Fix these fields:
              </p>
              <ul className="mt-1 list-disc pl-5">
                {failing.map((name) => (
                  <li key={name}>
                    <a href={`#${name}`} className="underline">
                      {FIELD_LABELS[name]}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <Field
            name="current_role"
            help="For example, Software Engineer."
            error={errors.current_role}
          >
            <Input
              id="current_role"
              name="current_role"
              value={values.current_role}
              maxLength={CURRENT_ROLE_MAX_LENGTH}
              autoComplete="organization-title"
              aria-invalid={Boolean(errors.current_role)}
              aria-describedby="current_role-message"
              onChange={(event) => change("current_role", event.target.value)}
              onBlur={() => blur("current_role")}
            />
          </Field>

          <Field
            name="career_level"
            help="How you would describe your level, for example Mid-level."
            error={errors.career_level}
          >
            <Input
              id="career_level"
              name="career_level"
              value={values.career_level}
              maxLength={CAREER_LEVEL_MAX_LENGTH}
              aria-invalid={Boolean(errors.career_level)}
              aria-describedby="career_level-message"
              onChange={(event) => change("career_level", event.target.value)}
              onBlur={() => blur("career_level")}
            />
          </Field>

          <Field
            name="years_of_experience"
            help="Total professional experience in years. Half years are allowed."
            error={errors.years_of_experience}
          >
            <Input
              id="years_of_experience"
              name="years_of_experience"
              type="number"
              inputMode="decimal"
              min={YEARS_MIN}
              max={YEARS_MAX}
              step={0.5}
              value={values.years_of_experience}
              aria-invalid={Boolean(errors.years_of_experience)}
              aria-describedby="years_of_experience-message"
              onChange={(event) =>
                change("years_of_experience", event.target.value)
              }
              onBlur={() => blur("years_of_experience")}
            />
          </Field>

          {saveError && (
            <p role="alert" className="text-destructive text-sm">
              {saveError}
            </p>
          )}
        </CardContent>

        <CardFooter className="mt-6 flex items-center justify-between gap-4">
          <p className="text-muted-foreground text-xs" aria-live="polite">
            {saving
              ? "Saving…"
              : savedAt
                ? `Last saved ${new Date(savedAt).toLocaleString()}`
                : "Not saved yet"}
          </p>
          <Button type="submit" disabled={saving}>
            {saving ? "Saving…" : "Save profile"}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}

function Field({
  name,
  help,
  error,
  children,
}: {
  name: FieldName;
  help: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-1.5">
      <Label htmlFor={name}>
        {FIELD_LABELS[name]}{" "}
        <span className="text-ink-subtle font-normal">Optional</span>
      </Label>
      {children}
      <p
        id={`${name}-message`}
        className={
          error ? "text-destructive text-xs" : "text-muted-foreground text-xs"
        }
      >
        {error ?? help}
      </p>
    </div>
  );
}
