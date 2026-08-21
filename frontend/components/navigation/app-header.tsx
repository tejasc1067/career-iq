"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { SessionStatus } from "@/components/auth/session-status";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/", label: "Home" },
  { href: "/profile", label: "My Profile" },
];

export function AppHeader() {
  const pathname = usePathname();

  return (
    <header className="bg-card sticky top-0 z-10 border-b">
      <div className="mx-auto flex h-14 max-w-[1120px] items-center gap-6 px-4 md:px-6">
        <Link href="/" className="font-heading text-sm font-semibold">
          CareerIQ
        </Link>
        <nav aria-label="Main" className="flex items-center gap-1">
          {NAV_ITEMS.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "rounded-md px-2.5 py-1.5 text-sm",
                  active
                    ? "bg-accent text-accent-foreground font-medium"
                    : "text-muted-foreground hover:text-foreground",
                )}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="ml-auto">
          <SessionStatus />
        </div>
      </div>
    </header>
  );
}
