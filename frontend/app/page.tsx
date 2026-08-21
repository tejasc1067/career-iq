import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { SessionStatus } from "@/components/auth/session-status";
import { API_BASE_URL, fetchApiHealth } from "@/lib/api/client";

export default async function Home() {
  const api = await fetchApiHealth();

  return (
    <main className="flex flex-1 items-center justify-center p-6">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>CareerIQ</CardTitle>
          <CardDescription>
            Foundation is running. No product features are implemented yet.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <div className="flex items-center justify-between gap-4">
            <span className="text-muted-foreground">Frontend</span>
            <Badge variant="secondary">Running</Badge>
          </div>
          <div className="flex items-center justify-between gap-4">
            <span className="text-muted-foreground">Session</span>
            <SessionStatus />
          </div>
          <div className="flex items-center justify-between gap-4">
            <span className="text-muted-foreground">API</span>
            {api.ok ? (
              <Badge variant="secondary">
                Reachable &middot; v{api.health.version}
              </Badge>
            ) : (
              <Badge variant="destructive">Unreachable</Badge>
            )}
          </div>
          {!api.ok && (
            <p className="text-muted-foreground border-t pt-3">
              {api.error}. Start the API with{" "}
              <code className="font-mono text-foreground">
                uvicorn app.main:app --reload
              </code>{" "}
              in <code className="font-mono text-foreground">backend</code>.
            </p>
          )}
          <p className="text-ink-subtle border-t pt-3 font-mono text-xs">
            {API_BASE_URL}
          </p>
        </CardContent>
      </Card>
    </main>
  );
}
