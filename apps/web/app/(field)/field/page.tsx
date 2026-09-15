import Link from "next/link";
import { redirect } from "next/navigation";

import { LogoutButton } from "@/components/logout-button";
import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { MaintenanceTicket, TicketPriority } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./field-dashboard.module.css";

const PRIORITY_RANK: Record<TicketPriority, number> = { urgent: 0, high: 1, medium: 2, low: 3 };

export default async function FieldStaffHomePage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const tickets = await backendFetch<MaintenanceTicket[]>("/maintenance/tickets");
  const myJobs = (tickets ?? [])
    .filter((t) => t.status !== "closed")
    .sort((a, b) => PRIORITY_RANK[a.priority] - PRIORITY_RANK[b.priority]);

  return (
    <main className={styles.main}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.headerTitle}>Welcome, {user.full_name ?? user.email}</h1>
          <p className={styles.headerSubtitle}>Field Staff</p>
        </div>
        <LogoutButton />
      </div>

      <section className={styles.section}>
        <h2 className={styles.heading}>My Jobs</h2>
        <div className={styles.list}>
          {myJobs.map((ticket) => (
            <Link key={ticket.id} href={`/field/tickets/${ticket.id}`} className={styles.item}>
              <div className={styles.itemTop}>
                <span>{ticket.category}</span>
                <span className={ui.badge}>{ticket.status.replace(/_/g, " ")}</span>
              </div>
              <p className={styles.itemAddress}>{ticket.description}</p>
              <p className={ui.faintText}>priority: {ticket.priority}</p>
            </Link>
          ))}
          {myJobs.length === 0 && <p className={ui.mutedText}>No jobs assigned right now.</p>}
        </div>
      </section>
    </main>
  );
}
