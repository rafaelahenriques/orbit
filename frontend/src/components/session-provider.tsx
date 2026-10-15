"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import type { ReactNode } from "react";

import { fetchCurrentUser, signOut as requestSignOut } from "@/lib/api";
import type { User } from "@/lib/api";

export type Session =
  | { status: "loading" }
  | { status: "signed-out" }
  | { status: "signed-in"; user: User }
  | { status: "error" };

type SessionContextValue = {
  session: Session;
  /** Asks the API again, e.g. after it could not be reached. */
  reload: () => void;
  /** Signs out of Orbit. Throws if the API could not be reached. */
  signOut: () => Promise<void>;
};

const SessionContext = createContext<SessionContextValue | null>(null);

async function loadSession(): Promise<Session> {
  try {
    const user = await fetchCurrentUser();
    return user ? { status: "signed-in", user } : { status: "signed-out" };
  } catch {
    return { status: "error" };
  }
}

/** Loads the signed-in user once, and shares it with every component below. */
export function SessionProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session>({ status: "loading" });

  useEffect(() => {
    let ignore = false;
    loadSession().then((loaded) => {
      if (!ignore) setSession(loaded);
    });
    return () => {
      ignore = true;
    };
  }, []);

  const reload = useCallback(() => {
    setSession({ status: "loading" });
    loadSession().then(setSession);
  }, []);

  const signOut = useCallback(async () => {
    await requestSignOut();
    setSession({ status: "signed-out" });
  }, []);

  return (
    <SessionContext value={{ session, reload, signOut }}>
      {children}
    </SessionContext>
  );
}

export function useSession(): SessionContextValue {
  const value = useContext(SessionContext);
  if (!value) {
    throw new Error("useSession must be used inside a SessionProvider");
  }
  return value;
}
