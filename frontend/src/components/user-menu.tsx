"use client";

import { LogOut, RefreshCw } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { secondaryButton } from "@/components/button-styles";
import { useSession } from "@/components/session-provider";

const iconButton =
  "flex size-9 shrink-0 items-center justify-center rounded-md text-zinc-600 transition-colors hover:bg-zinc-200/60 hover:text-zinc-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:cursor-not-allowed disabled:opacity-60 dark:text-zinc-400 dark:hover:bg-zinc-800/60 dark:hover:text-zinc-100";

/** The signed-in user and a sign-out button, or a sign-in link. */
export function UserMenu() {
  const { session, reload, signOut } = useSession();
  const router = useRouter();
  const [signingOut, setSigningOut] = useState(false);
  const [signOutFailed, setSignOutFailed] = useState(false);

  async function handleSignOut() {
    setSigningOut(true);
    setSignOutFailed(false);
    try {
      await signOut();
      router.push("/sign-in");
    } catch {
      setSignOutFailed(true);
    } finally {
      setSigningOut(false);
    }
  }

  if (session.status === "loading") {
    return (
      <div
        aria-hidden
        className="size-9 animate-pulse rounded-full bg-zinc-200 md:h-9 md:w-full md:rounded-md dark:bg-zinc-800"
      />
    );
  }

  if (session.status === "error") {
    return (
      <div className="flex flex-col gap-2">
        <p className="sr-only text-xs text-zinc-600 md:not-sr-only dark:text-zinc-400">
          Can&apos;t load your account.
        </p>
        <button type="button" onClick={reload} className={secondaryButton}>
          <RefreshCw aria-hidden className="size-4" />
          Retry
        </button>
      </div>
    );
  }

  if (session.status === "signed-out") {
    return (
      <Link href="/sign-in" className={`${secondaryButton} w-full`}>
        Sign in
      </Link>
    );
  }

  const { user } = session;
  return (
    <div>
      <div className="flex items-center gap-3">
        <span
          aria-hidden
          className="flex size-8 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-sm font-medium text-indigo-700 dark:bg-indigo-500/20 dark:text-indigo-300"
        >
          {(user.name ?? user.email).charAt(0).toUpperCase()}
        </span>
        <div className="sr-only min-w-0 flex-1 md:not-sr-only">
          <p className="truncate text-sm font-medium">
            {user.name ?? user.email}
          </p>
          {user.name && (
            <p className="truncate text-xs text-zinc-600 dark:text-zinc-400">
              {user.email}
            </p>
          )}
        </div>
        <button
          type="button"
          onClick={handleSignOut}
          disabled={signingOut}
          title="Sign out"
          className={iconButton}
        >
          <LogOut aria-hidden className="size-4" />
          <span className="sr-only">
            {signingOut ? "Signing out…" : "Sign out"}
          </span>
        </button>
      </div>
      {signOutFailed && (
        <p role="alert" className="mt-2 text-xs text-red-700 dark:text-red-400">
          Couldn&apos;t sign out. Try again.
        </p>
      )}
    </div>
  );
}
