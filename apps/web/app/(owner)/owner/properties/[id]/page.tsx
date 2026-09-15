import { notFound, redirect } from "next/navigation";

import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { DocumentRecord, Property } from "@/lib/types";

import { DocumentVault } from "./document-vault";
import styles from "./property-detail.module.css";

export default async function PropertyDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const { id } = await params;
  const [property, documents] = await Promise.all([
    backendFetch<Property>(`/properties/${id}`),
    backendFetch<DocumentRecord[]>(`/documents?owner_type=property&owner_id=${id}`),
  ]);

  if (!property) notFound();

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

      <DocumentVault propertyId={property.id} initialDocuments={documents ?? []} />
    </main>
  );
}
