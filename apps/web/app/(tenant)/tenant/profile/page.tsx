import { redirect } from "next/navigation";

import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { TenantProfile } from "@/lib/types";

import { ProfileForm } from "./profile-form";
import styles from "./profile.module.css";

export default async function TenantProfilePage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const profile = await backendFetch<TenantProfile>("/tenant/profile");

  return (
    <main className={styles.main}>
      <h1 className={styles.title}>Tenant Profile</h1>
      <ProfileForm initialProfile={profile} />
    </main>
  );
}
