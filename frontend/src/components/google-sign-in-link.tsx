import type { ReactNode } from "react";

import { primaryButton } from "@/components/button-styles";
import { googleSignInUrl } from "@/lib/api";

type GoogleSignInLinkProps = {
  /** Shows Google's consent screen again, to grant access that was skipped. */
  reconnect?: boolean;
  className?: string;
  children: ReactNode;
};

export function GoogleSignInLink({
  reconnect = false,
  className = "",
  children,
}: GoogleSignInLinkProps) {
  // A plain link rather than next/link: signing in leaves the app for Google.
  return (
    <a
      href={googleSignInUrl({ reconnect })}
      className={`${primaryButton} ${className}`}
    >
      {children}
    </a>
  );
}
