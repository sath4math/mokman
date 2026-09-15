import Link from "next/link";
import { redirect } from "next/navigation";

import { LogoutButton } from "@/components/logout-button";
import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { MaintenanceTicket } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./tickets.module.css";

export default async function AdminTicketsPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const tickets = await backendFetch<MaintenanceTicket[]>("/maintenance/tickets");

  return (
    <main className={styles.main}>
      <div className={ui.flexBetween}>
        <h1 className={styles.title}>Tickets</h1>
        <LogoutButton />
      </div>
      <ul className={styles.list}>
        {(tickets ?? []).map((ticket) => (
          <li key={ticket.id}>
            <Link href={`/admin/tickets/${ticket.id}`} className={styles.item}>
              <div className={styles.itemInfo}>
                <span>
                  {ticket.category} — {ticket.description.slice(0, 60)}
                </span>
                <span className={ui.faintText}>priority: {ticket.priority}</span>
              </div>
              <span className={ui.badge}>{ticket.status.replace(/_/g, " ")}</span>
            </Link>
          </li>
        ))}
        {(!tickets || tickets.length === 0) && <p className={ui.mutedText}>No tickets yet.</p>}
      </ul>
    </main>
  );
}
