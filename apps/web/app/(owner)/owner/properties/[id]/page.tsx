import Link from "next/link";
import { notFound, redirect } from "next/navigation";

import { DocumentVault } from "@/components/document-vault";
import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type {
  ComplianceDue,
  DocumentRecord,
  Expense,
  Lease,
  MaintenanceSchedule,
  MaintenanceTicket,
  Property,
  PropertyStatement,
  UtilityConnection,
} from "@/lib/types";
import ui from "@/styles/ui.module.css";

import { CompliancePanel } from "./compliance-panel";
import { ExpensesPanel } from "./expenses-panel";
import { PreventiveMaintenancePanel } from "./preventive-maintenance-panel";
import styles from "./property-detail.module.css";
import { TicketsPanel } from "./tickets-panel";
import { UtilitiesPanel } from "./utilities-panel";

export default async function PropertyDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const { id } = await params;
  const [property, documents, leases, statement, expenses, tickets, schedules, utilityConnections, complianceDues] =
    await Promise.all([
      backendFetch<Property>(`/properties/${id}`),
      backendFetch<DocumentRecord[]>(`/documents?owner_type=property&owner_id=${id}`),
      backendFetch<Lease[]>("/leases"),
      backendFetch<PropertyStatement>(`/finance/statement?property_id=${id}`),
      backendFetch<Expense[]>(`/expenses?property_id=${id}`),
      backendFetch<MaintenanceTicket[]>(`/maintenance/tickets?property_id=${id}`),
      backendFetch<MaintenanceSchedule[]>(`/maintenance-schedules?property_id=${id}`),
      backendFetch<UtilityConnection[]>(`/utilities/connections?property_id=${id}`),
      backendFetch<ComplianceDue[]>(`/compliance/dues?property_id=${id}`),
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

      <section className={styles.leaseSection}>
        <h2 className={styles.leaseHeading}>Finances</h2>
        {statement ? (
          <div className={ui.card}>
            <div className={ui.flexCol}>
              <p>
                Rent collected: <strong>{statement.rent_collected}</strong>
              </p>
              <p>
                Expenses: <strong>{statement.expenses}</strong>
              </p>
              <p>
                Mokman fee: <strong>{statement.mokman_fee}</strong>
              </p>
              <p>
                Net payable: <strong>{statement.net_payable}</strong>
              </p>
            </div>
            <Link href={`/owner/properties/${property.id}/statement`} className={ui.link}>
              View full statement →
            </Link>
          </div>
        ) : (
          <p className={ui.mutedText}>No financial activity yet this month.</p>
        )}
      </section>

      <ExpensesPanel propertyId={property.id} initialExpenses={expenses ?? []} />

      <TicketsPanel propertyId={property.id} initialTickets={tickets ?? []} />

      <PreventiveMaintenancePanel propertyId={property.id} initialSchedules={schedules ?? []} />

      <UtilitiesPanel propertyId={property.id} initialConnections={utilityConnections ?? []} />

      <CompliancePanel propertyId={property.id} initialDues={complianceDues ?? []} />

      <DocumentVault
        ownerType="property"
        ownerId={property.id}
        initialDocuments={documents ?? []}
        documentTypes={["noc", "society_notice", "tax_receipt", "utility_bill", "other"]}
      />
    </main>
  );
}
