import Link from "next/link";
import { notFound, redirect } from "next/navigation";

import { DocumentVault } from "@/components/document-vault";
import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { DocumentRecord, Property } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "../../owner-detail.module.css";

export default async function AdminPropertyDetailPage({
  params,
}: {
  params: Promise<{ ownerId: string; propertyId: string }>;
}) {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const { ownerId, propertyId } = await params;
  const [property, documents] = await Promise.all([
    backendFetch<Property>(`/properties/${propertyId}`),
    backendFetch<DocumentRecord[]>(`/documents?owner_type=property&owner_id=${propertyId}`),
  ]);
  if (!property) notFound();

  return (
    <main className={styles.main}>
      <div className={ui.flexBetween}>
        <h1 className={styles.title}>{property.name}</h1>
        <Link href={`/admin/owners/${ownerId}`} className={ui.link}>
          back to owner
        </Link>
      </div>
      <p className={ui.mutedText}>
        {property.category} — {property.address_line}, {property.city}, {property.state}{" "}
        {property.postal_code}
      </p>
      <span className={ui.badge}>{property.status}</span>

      <section className={styles.section}>
        <h2 className={ui.badge}>Photos & videos</h2>
        <DocumentVault
          ownerType="property"
          ownerId={property.id}
          initialDocuments={documents ?? []}
          documentTypes={["photo", "video", "floor_plan", "other"]}
        />
      </section>
    </main>
  );
}
