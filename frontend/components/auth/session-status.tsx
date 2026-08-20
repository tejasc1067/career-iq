"use client";

import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth/context";

export function SessionStatus() {
  const { status, signOut } = useAuth();

  if (status === "loading") {
    return <Badge variant="secondary">Checking…</Badge>;
  }

  if (status === "authenticated") {
    return (
      <span className="flex items-center gap-2">
        <Badge variant="secondary">Signed in</Badge>
        <Button size="sm" variant="ghost" onClick={() => signOut()}>
          Sign out
        </Button>
      </span>
    );
  }

  return (
    <span className="flex items-center gap-2">
      <Badge variant="outline">Signed out</Badge>
      <Button size="sm" variant="ghost" asChild>
        <Link href="/login">Sign in</Link>
      </Button>
    </span>
  );
}
