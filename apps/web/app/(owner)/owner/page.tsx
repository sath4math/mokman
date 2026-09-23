import Link from "next/link";

import { LogoutButton } from "@/components/logout-button";
import { backendFetch } from "@/lib/backend";
import { requireVerifiedOwner } from "@/lib/current-user";
import type { OwnerProfile, Property } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./owner-dashboard.module.css";

export default async function OwnerDashboardPage() {
  const user = await requireVerifiedOwner();

  const [profile, properties] = await Promise.all([
    backendFetch<OwnerProfile>("/owner/profile"),
    backendFetch<Property[]>("/properties"),
  ]);

  return (
    <main className={styles.main}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.headerTitle}>Welcome, {user.full_name ?? user.email}</h1>
          <p className={styles.headerSubtitle}>Owner dashboard</p>
        </div>
        <LogoutButton />
      </div>

      <section className={styles.kycBanner}>
        <p>
          KYC status: <strong>{profile?.kyc_status ?? "not started"}</strong>
        </p>
        <Link href="/owner/profile" className={ui.link}>
          {profile ? "Edit profile" : "Complete your profile"}
        </Link>
        <Link href="/owner/assistant" className={ui.link}>
          Ask the Owner Assistant
        </Link>
        <Link href="/owner/insights" className={ui.link}>
          View Insights
        </Link>
      </section>

      <section className={styles.propertiesSection}>
        <div className={styles.propertiesHeader}>
          <h2 className={styles.propertiesHeading}>Your properties</h2>
          <Link href="/owner/properties/new" className={`${ui.btnPrimary} ${ui.btnSmall}`}>
            Add Property
          </Link>
        </div>

        {properties && properties.length > 0 ? (
          <ul className={styles.propertyGrid}>
            {properties.map((property) => (
              <li key={property.id}>
                <Link href={`/owner/properties/${property.id}`} className={styles.propertyCard}>
                  <div className={styles.propertyTop}>
                    <span className={styles.propertyName}>{property.name}</span>
                    <span className={styles.propertyStatus}>{property.status}</span>
                  </div>
                  <p className={styles.propertyAddress}>
                    {property.address_line}, {property.city}
                  </p>
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p className={ui.mutedText}>No properties yet — add your first one.</p>
        )}
      </section>
    </main>
  );
}
