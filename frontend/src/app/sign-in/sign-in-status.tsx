"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect } from "react";

import { useSession } from "@/components/session-provider";

// The API sends people back here with one of these codes when sign-in fails.
const ERROR_MESSAGES: Record<string, string> = {
  // Only seen in development: production refuses to start without Google set up.
  not_configured:
    "Google sign-in isn't set up yet. Add your Google OAuth client to .env (see the README), then restart the API.",
  access_denied: "Sign-in was cancelled. Try again when you're ready.",
  session_expired: "Sign-in took too long. Please try again.",
  email_not_verified:
    "Your Google account's email address isn't verified. Verify it with Google, then try again.",
  google_error: "Google couldn't sign you in. Please try again.",
};

export function SignInError() {
  const error = useSearchParams().get("error");
  if (!error) return null;

  return (
    <p
      role="alert"
      className="mt-6 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800 dark:border-red-900/60 dark:bg-red-950/40 dark:text-red-300"
    >
      {ERROR_MESSAGES[error] ?? ERROR_MESSAGES.google_error}
    </p>
  );
}

/** Sends people who are already signed in to the dashboard. */
export function RedirectWhenSignedIn() {
  const { session } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (session.status === "signed-in") router.replace("/");
  }, [session.status, router]);

  return null;
}
