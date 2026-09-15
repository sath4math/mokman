import { cookies } from "next/headers";

import { API_BASE_URL, SESSION_COOKIE } from "@/lib/session";

/** Server-side authenticated GET against the API, for use in Server Components. */
export async function backendFetch<T>(path: string): Promise<T | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get(SESSION_COOKIE)?.value;
  if (!token) return null;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!response.ok) return null;

  return response.json() as Promise<T>;
}
