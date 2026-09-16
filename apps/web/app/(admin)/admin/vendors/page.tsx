import { redirect } from "next/navigation";

import { LogoutButton } from "@/components/logout-button";
import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { Vendor } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import { AdminVendorsPanel } from "./admin-vendors-panel";
import styles from "./vendors.module.css";

export default async function AdminVendorsPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const vendors = await backendFetch<Vendor[]>("/vendors");

  return (
    <main className={styles.main}>
      <div className={ui.flexBetween}>
        <h1 className={styles.title}>Vendors</h1>
        <LogoutButton />
      </div>
      <AdminVendorsPanel initialVendors={vendors ?? []} />
    </main>
  );
}
