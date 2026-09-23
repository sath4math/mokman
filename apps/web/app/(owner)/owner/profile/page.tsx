import { redirect } from "next/navigation";

import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { AuthorizedRepresentative, DocumentRecord, OwnerProfile } from "@/lib/types";

import { ProfileForm } from "./profile-form";
import styles from "./profile.module.css";

export default async function OwnerProfilePage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const [profile, representatives, documents] = await Promise.all([
    backendFetch<OwnerProfile>("/owner/profile"),
    backendFetch<AuthorizedRepresentative[]>("/owner/profile/representatives"),
    backendFetch<DocumentRecord[]>(`/documents?owner_type=owner_profile&owner_id=${user.id}`),
  ]);

  return (
    <main className={styles.main}>
      <h1 className={styles.title}>Owner Profile</h1>
      <ProfileForm
        ownerId={user.id}
        initialProfile={profile}
        initialRepresentatives={representatives ?? []}
        initialDocuments={documents ?? []}
      />
    </main>
  );
}
