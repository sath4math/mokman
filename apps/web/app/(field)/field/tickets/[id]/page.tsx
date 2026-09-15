import { notFound, redirect } from "next/navigation";

import { TicketDetail } from "@/components/ticket-detail";
import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { DocumentRecord, MaintenanceTicket } from "@/lib/types";

import styles from "./ticket-page.module.css";

export default async function FieldTicketDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const { id } = await params;
  const ticket = await backendFetch<MaintenanceTicket>(`/maintenance/tickets/${id}`);
  if (!ticket) notFound();

  const documents = await backendFetch<DocumentRecord[]>(`/documents?owner_type=ticket&owner_id=${id}`);

  return (
    <main className={styles.main}>
      <TicketDetail
        ticket={ticket}
        viewerRole="field_staff"
        viewerId={user.id}
        documents={documents ?? []}
        staff={[]}
      />
    </main>
  );
}
