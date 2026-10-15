"use client";

import { CloudOff, Sparkles } from "lucide-react";

import { secondaryButton } from "@/components/button-styles";
import { EmptyState, EmptyStateSkeleton } from "@/components/empty-state";
import { GoogleSignInLink } from "@/components/google-sign-in-link";
import { useSession } from "@/components/session-provider";

export function BriefingEmptyState() {
  const { session, reload } = useSession();

  switch (session.status) {
    case "loading":
      return <EmptyStateSkeleton />;
    case "error":
      return (
        <EmptyState
          icon={CloudOff}
          title="Can't reach Orbit right now"
          description="Check your connection, then try again."
          action={
            <button type="button" onClick={reload} className={secondaryButton}>
              Try again
            </button>
          }
        />
      );
    case "signed-out":
      return (
        <EmptyState
          icon={Sparkles}
          title="Connect your Google account"
          description="Orbit reads your Gmail and Google Calendar to build your daily briefing. It never sends email or changes your calendar."
          action={<GoogleSignInLink>Connect Google</GoogleSignInLink>}
        />
      );
    case "signed-in":
      if (!session.user.google_connected) {
        return (
          <EmptyState
            icon={Sparkles}
            title="Finish connecting Google"
            description="Orbit needs read-only access to both Gmail and Google Calendar to build your briefing."
            action={
              <GoogleSignInLink reconnect>Connect Google</GoogleSignInLink>
            }
          />
        );
      }
      return (
        <EmptyState
          icon={Sparkles}
          title="Your briefing will appear here"
          description="Orbit will summarise your day here each morning."
        />
      );
  }
}
