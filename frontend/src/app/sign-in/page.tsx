import { Orbit } from "lucide-react";
import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

import { GoogleSignInLink } from "@/components/google-sign-in-link";

import { RedirectWhenSignedIn, SignInError } from "./sign-in-status";

export const metadata: Metadata = {
  title: "Sign in",
};

export default function SignInPage() {
  return (
    <main
      id="main"
      className="flex min-h-dvh items-center justify-center px-4 py-12"
    >
      <RedirectWhenSignedIn />
      <div className="w-full max-w-sm">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-lg font-semibold tracking-tight"
        >
          <Orbit
            aria-hidden
            className="size-5 text-indigo-600 dark:text-indigo-400"
          />
          Orbit
        </Link>
        <h1 className="mt-8 text-2xl font-semibold tracking-tight">
          Sign in to Orbit
        </h1>
        <p className="mt-2 text-zinc-600 dark:text-zinc-400">
          Your email, calendar, and news in one daily briefing.
        </p>

        {/* The error comes from the URL, which is only known in the browser. */}
        <Suspense>
          <SignInError />
        </Suspense>

        <GoogleSignInLink className="mt-8 w-full">
          Continue with Google
        </GoogleSignInLink>
        <p className="mt-4 text-sm text-zinc-600 dark:text-zinc-400">
          Orbit asks for read-only access to Gmail and Google Calendar. It never
          sends email or changes your calendar.
        </p>
      </div>
    </main>
  );
}
