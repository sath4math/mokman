import Link from "next/link";
import { redirect } from "next/navigation";

import { LogoutButton } from "@/components/logout-button";
import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { Lease, RentInvoice, TenantProfile } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./tenant-dashboard.module.css";

export default async function TenantHomePage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const [profile, leases] = await Promise.all([
    backendFetch<TenantProfile>("/tenant/profile"),
    backendFetch<Lease[]>("/leases"),
  ]);

  const activeLeases = (leases ?? []).filter(
    (lease) => lease.status !== "terminated" && lease.status !== "expired",
  );

  const nextInvoiceByLease = new Map<string, RentInvoice | undefined>();
  await Promise.all(
    activeLeases
      .filter((lease) => lease.status === "active")
      .map(async (lease) => {
        const invoices = await backendFetch<RentInvoice[]>(`/rent/invoices?lease_id=${lease.id}`);
        nextInvoiceByLease.set(
          lease.id,
          invoices?.find((inv) => inv.status !== "paid" && inv.status !== "cancelled"),
        );
      }),
  );

  return (
    <main className={styles.main}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.headerTitle}>Welcome, {user.full_name ?? user.email}</h1>
          <p className={styles.headerSubtitle}>Tenant home</p>
        </div>
        <LogoutButton />
      </div>

      <section className={styles.profileBanner}>
        <p>
          Verification status: <strong>{profile?.verification_status ?? "not started"}</strong>
        </p>
        <Link href="/tenant/profile" className={ui.link}>
          {profile ? "Edit profile" : "Complete your profile"}
        </Link>
      </section>

      <section className={styles.leaseSection}>
        <h2 className={styles.leaseHeading}>Your lease</h2>
        {activeLeases.length > 0 ? (
          <ul className={ui.flexCol}>
            {activeLeases.map((lease) => (
              <li key={lease.id}>
                <Link href={`/tenant/leases/${lease.id}`} className={styles.leaseCard}>
                  <div className={styles.leaseTop}>
                    <span>
                      {lease.start_date} – {lease.end_date}
                    </span>
                    <span className={styles.leaseStatus}>{lease.status.replace(/_/g, " ")}</span>
                  </div>
                  <p className={styles.leaseRent}>Monthly rent: {lease.monthly_rent}</p>
                  {lease.status === "pending_acknowledgment" && !lease.tenant_acknowledged_at && (
                    <p className={ui.errorText}>Action needed: acknowledge this lease</p>
                  )}
                  {nextInvoiceByLease.get(lease.id) && (
                    <p className={ui.faintText}>
                      Next payment due {nextInvoiceByLease.get(lease.id)!.due_date}:{" "}
                      {nextInvoiceByLease.get(lease.id)!.amount_due} (
                      {nextInvoiceByLease.get(lease.id)!.status.replace(/_/g, " ")})
                    </p>
                  )}
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p className={ui.mutedText}>No lease yet — your owner will add you once a property is ready.</p>
        )}
      </section>
    </main>
  );
}
