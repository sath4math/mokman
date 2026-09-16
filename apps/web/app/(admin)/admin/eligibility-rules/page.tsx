import { redirect } from "next/navigation";

import { LogoutButton } from "@/components/logout-button";
import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { ServiceCategory } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import { AdminEligibilityRulesPanel } from "./admin-eligibility-rules-panel";
import styles from "./eligibility-rules.module.css";

export default async function AdminEligibilityRulesPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const categories = await backendFetch<ServiceCategory[]>("/maintenance/service-categories");

  return (
    <main className={styles.main}>
      <div className={ui.flexBetween}>
        <h1 className={styles.title}>Eligibility rules</h1>
        <LogoutButton />
      </div>
      <AdminEligibilityRulesPanel categories={categories ?? []} />
    </main>
  );
}
