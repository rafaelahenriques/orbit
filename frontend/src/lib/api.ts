// The API runs on its own origin. Requests include credentials so the browser sends
// the session cookie, which is httpOnly: JavaScript can never read it.
export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type User = {
  id: string;
  email: string;
  name: string | null;
  /** False until the user grants read-only Gmail and Calendar access. */
  google_connected: boolean;
};

/** Returns the signed-in user, or null when nobody is signed in. */
export async function fetchCurrentUser(): Promise<User | null> {
  const response = await fetch(`${API_URL}/api/auth/me`, {
    credentials: "include",
  });
  if (response.status === 401) return null;
  if (!response.ok) {
    throw new Error(`Could not load the signed-in user (${response.status})`);
  }
  return response.json();
}

export async function signOut(): Promise<void> {
  const response = await fetch(`${API_URL}/api/auth/logout`, {
    method: "POST",
    credentials: "include",
  });
  if (!response.ok) throw new Error(`Could not sign out (${response.status})`);
}

/**
 * The API route that starts "Sign in with Google". `reconnect` shows Google's consent
 * screen again, so people can grant access they skipped the first time.
 */
export function googleSignInUrl({ reconnect = false } = {}): string {
  const url = `${API_URL}/api/auth/google/login`;
  return reconnect ? `${url}?reconnect=true` : url;
}
