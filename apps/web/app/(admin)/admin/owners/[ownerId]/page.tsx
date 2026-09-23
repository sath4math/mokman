import Link from "next/link";
import { redirect } from "next/navigation";

import { ProfileForm } from "@/app/(owner)/owner/profile/profile-form";
import { LogoutButton } from "@/components/logout-button";
import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { DocumentRecord, OwnerProfileAdmin, Property } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./owner-detail.module.css";

export default async function AdminOwnerDetailPage({
  params,
}: {
  params: Promise<{ ownerId: string }>;
}) {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const { ownerId } = await params;
  const [profile, documents, properties] = await Promise.all([
    backendFetch<OwnerProfileAdmin>(`/owner/profiles/${ownerId}`),
    backendFetch<DocumentRecord[]>(`/documents?owner_type=owner_profile&owner_id=${ownerId}`),
    backendFetch<Property[]>(`/properties?owner_id=${ownerId}`),
  ]);

  return (
    <main className={styles.main}>
      <div className={ui.flexBetween}>
        <h1 className={styles.title}>
          Manage owner{profile?.full_name ? `: ${profile.full_name}` : ""}
        </h1>
        <LogoutButton />
      </div>
      <p className={ui.mutedText}>
        {profile?.email ?? "no email"} —{" "}
        <Link href="/admin/kyc" className={ui.link}>
          back to KYC review
        </Link>
      </p>

      <section className={styles.section}>
        <h2 className={ui.badge}>KYC (on behalf of owner)</h2>
        <ProfileForm
          ownerId={ownerId}
          mode="admin"
          initialProfile={profile}
          initialRepresentatives={[]}
          initialDocuments={documents ?? []}
        />
      </section>

      <section className={styles.section}>
        <div className={ui.flexBetween}>
          <h2 className={ui.badge}>Properties</h2>
          <Link href={`/admin/owners/${ownerId}/properties/new`} className={`${ui.btnPrimary} ${ui.btnSmall}`}>
            Add property
          </Link>
        </div>
        <ul className={styles.list}>
          {(properties ?? []).map((property) => (
            <li key={property.id} className={styles.item}>
              <Link href={`/admin/owners/${ownerId}/properties/${property.id}`} className={ui.linkPrimary}>
                {property.name} — {property.city}
              </Link>
              <span className={ui.badge}>{property.status}</span>
            </li>
          ))}
          {(!properties || properties.length === 0) && (
            <p className={ui.mutedText}>No properties registered for this owner yet.</p>
          )}
        </ul>
      </section>
    </main>
  );
}
