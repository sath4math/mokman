import { notFound, redirect } from "next/navigation";

import { LeaseDetail } from "@/components/lease-detail";
import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { DocumentRecord, Inspection, Lease, RentInvoice } from "@/lib/types";

import styles from "./lease-page.module.css";

export default async function OwnerLeaseDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const { id } = await params;
  const lease = await backendFetch<Lease>(`/leases/${id}`);
  if (!lease) notFound();

  const [documents, inspections, invoices] = await Promise.all([
    backendFetch<DocumentRecord[]>(`/documents?owner_type=lease&owner_id=${id}`),
    backendFetch<Inspection[]>(`/inspections?property_id=${lease.property_id}&lease_id=${id}`),
    backendFetch<RentInvoice[]>(`/rent/invoices?lease_id=${id}`),
  ]);

  return (
    <main className={styles.main}>
      <LeaseDetail
        lease={lease}
        viewerRole="owner"
        documents={documents ?? []}
        inspections={inspections ?? []}
        invoices={invoices ?? []}
      />
    </main>
  );
}
