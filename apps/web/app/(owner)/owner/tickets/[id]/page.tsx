import { notFound } from "next/navigation";

import { TicketDetail } from "@/components/ticket-detail";
import { backendFetch } from "@/lib/backend";
import { requireVerifiedOwner } from "@/lib/current-user";
import type { DocumentRecord, FieldStaffUser, MaintenanceTicket, Vendor } from "@/lib/types";

import styles from "./ticket-page.module.css";

export default async function OwnerTicketDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const user = await requireVerifiedOwner();

  const { id } = await params;
  const ticket = await backendFetch<MaintenanceTicket>(`/maintenance/tickets/${id}`);
  if (!ticket) notFound();

  const [documents, staff, vendors] = await Promise.all([
    backendFetch<DocumentRecord[]>(`/documents?owner_type=ticket&owner_id=${id}`),
    backendFetch<FieldStaffUser[]>("/maintenance/staff"),
    backendFetch<Vendor[]>("/vendors?active_only=true"),
  ]);

  return (
    <main className={styles.main}>
      <TicketDetail
        ticket={ticket}
        viewerRole="owner"
        viewerId={user.id}
        documents={documents ?? []}
        staff={staff ?? []}
        vendors={vendors ?? []}
      />
    </main>
  );
}
