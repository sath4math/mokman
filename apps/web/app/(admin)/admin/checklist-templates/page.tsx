import { redirect } from "next/navigation";

import { LogoutButton } from "@/components/logout-button";
import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { ChecklistTemplate } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import { AdminChecklistTemplatesPanel } from "./admin-checklist-templates-panel";
import styles from "./checklist-templates.module.css";

export default async function AdminChecklistTemplatesPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const templates = await backendFetch<ChecklistTemplate[]>("/maintenance/checklist-templates");

  return (
    <main className={styles.main}>
      <div className={ui.flexBetween}>
        <h1 className={styles.title}>Checklist templates</h1>
        <LogoutButton />
      </div>
      <AdminChecklistTemplatesPanel initialTemplates={templates ?? []} />
    </main>
  );
}
