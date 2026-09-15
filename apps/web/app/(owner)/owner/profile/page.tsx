import { redirect } from "next/navigation";

import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { AuthorizedRepresentative, OwnerProfile } from "@/lib/types";

import { ProfileForm } from "./profile-form";
import styles from "./profile.module.css";

export default async function OwnerProfilePage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const [profile, representatives] = await Promise.all([
    backendFetch<OwnerProfile>("/owner/profile"),
    backendFetch<AuthorizedRepresentative[]>("/owner/profile/representatives"),
  ]);

  return (
    <main className={styles.main}>
      <h1 className={styles.title}>Owner Profile</h1>
      <ProfileForm initialProfile={profile} initialRepresentatives={representatives ?? []} />
    </main>
  );
}
