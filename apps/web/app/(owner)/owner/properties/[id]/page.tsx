import Link from "next/link";
import { notFound, redirect } from "next/navigation";

import { DocumentVault } from "@/components/document-vault";
import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { DocumentRecord, Lease, Property } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./property-detail.module.css";

export default async function PropertyDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const { id } = await params;
  const [property, documents, leases] = await Promise.all([
    backendFetch<Property>(`/properties/${id}`),
    backendFetch<DocumentRecord[]>(`/documents?owner_type=property&owner_id=${id}`),
    backendFetch<Lease[]>("/leases"),
  ]);

  if (!property) notFound();

  const propertyLease = leases?.find(
    (lease) => lease.property_id === id && lease.status !== "terminated" && lease.status !== "expired",
  );

  return (
    <main className={styles.main}>
      <div>
        <div className={styles.titleRow}>
          <h1 className={styles.title}>{property.name}</h1>
          <span className={styles.status}>{property.status}</span>
        </div>
        <p className={styles.address}>
          {property.address_line}, {property.city}, {property.state} {property.postal_code}
        </p>
      </div>

      <section className={styles.factsGrid}>
        <div>
          <div className={styles.factLabel}>Category</div>
          <div>{property.category}</div>
        </div>
        <div>
          <div className={styles.factLabel}>Area</div>
          <div>{property.area_sqft ? `${property.area_sqft} sqft` : "—"}</div>
        </div>
        <div>
          <div className={styles.factLabel}>Floors</div>
          <div>{property.num_floors ?? "—"}</div>
        </div>
        <div>
          <div className={styles.factLabel}>Units</div>
          <div>{property.num_units ?? "—"}</div>
        </div>
        <div className={styles.factSpan2}>
          <div className={styles.factLabel}>Amenities</div>
          <div>{property.amenities?.join(", ") || "—"}</div>
        </div>
        <div>
          <div className={styles.factLabel}>Furnishing</div>
          <div>{property.furnishing_status ?? "—"}</div>
        </div>
      </section>

      <section className={styles.leaseSection}>
        <h2 className={styles.leaseHeading}>Tenancy</h2>
        {propertyLease ? (
          <Link href={`/owner/leases/${propertyLease.id}`} className={ui.card}>
            <div className={ui.flexBetween}>
              <span>Lease status: {propertyLease.status}</span>
              <span className={ui.link}>View lease →</span>
            </div>
          </Link>
        ) : (
          <div className={ui.flexBetween}>
            <p className={ui.mutedText}>No active lease on this property.</p>
            <Link href={`/owner/leases/new?property_id=${property.id}`} className={`${ui.btnPrimary} ${ui.btnSmall}`}>
              Create Lease
            </Link>
          </div>
        )}
      </section>

      <DocumentVault ownerType="property" ownerId={property.id} initialDocuments={documents ?? []} />
    </main>
  );
}
