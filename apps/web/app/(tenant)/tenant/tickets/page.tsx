import { redirect } from "next/navigation";

import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { Lease, MaintenanceTicket, Property } from "@/lib/types";

import styles from "./tickets.module.css";
import { TenantTicketsPanel } from "./tenant-tickets-panel";

export default async function TenantTicketsPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const [leases, tickets] = await Promise.all([
    backendFetch<Lease[]>("/leases"),
    backendFetch<MaintenanceTicket[]>("/maintenance/tickets"),
  ]);

  const activeLeases = (leases ?? []).filter(
    (lease) => lease.status !== "terminated" && lease.status !== "expired",
  );

  const properties = await Promise.all(
    activeLeases.map(async (lease) => {
      const property = await backendFetch<Property>(`/properties/${lease.property_id}`);
      return { id: lease.property_id, label: property?.name ?? `Property (lease ${lease.start_date})` };
    }),
  );

  return (
    <main className={styles.main}>
      <h1 className={styles.title}>Maintenance</h1>
      <TenantTicketsPanel properties={properties} initialTickets={tickets ?? []} />
    </main>
  );
}
