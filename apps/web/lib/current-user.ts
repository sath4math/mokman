import { cookies } from "next/headers";

import { API_BASE_URL, SESSION_COOKIE, type CurrentUser } from "@/lib/session";

export async function getCurrentUser(): Promise<CurrentUser | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get(SESSION_COOKIE)?.value;
  if (!token) return null;

  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!response.ok) return null;

  return response.json() as Promise<CurrentUser>;
}
