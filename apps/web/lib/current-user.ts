import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { backendFetch } from "@/lib/backend";
import { API_BASE_URL, SESSION_COOKIE, type CurrentUser } from "@/lib/session";
import type { OwnerProfile } from "@/lib/types";

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

/**
 * Auth check for owner pages that require completed, admin-verified KYC.
 * An owner whose KYC isn't verified yet is redirected to /owner/kyc-pending
 * -- they can only reach their own /owner/profile until an admin approves.
 * Non-owner roles that somehow land on an owner page are left ungated here
 * (the backend itself enforces role access on every underlying call).
 */
export async function requireVerifiedOwner(): Promise<CurrentUser> {
  const user = await getCurrentUser();
  if (!user) redirect("/login");
  if (user.role === "owner") {
    const profile = await backendFetch<OwnerProfile>("/owner/profile");
    if (!profile || profile.kyc_status !== "verified") {
      redirect("/owner/kyc-pending");
    }
  }
  return user;
}
