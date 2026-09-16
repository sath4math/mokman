import { redirect } from "next/navigation";

import { LogoutButton } from "@/components/logout-button";
import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { ServiceCategory } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import { AdminServiceCategoriesPanel } from "./admin-service-categories-panel";
import styles from "./service-categories.module.css";

export default async function AdminServiceCategoriesPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const categories = await backendFetch<ServiceCategory[]>("/maintenance/service-categories");

  return (
    <main className={styles.main}>
      <div className={ui.flexBetween}>
        <h1 className={styles.title}>Service categories</h1>
        <LogoutButton />
      </div>
      <AdminServiceCategoriesPanel initialCategories={categories ?? []} />
    </main>
  );
}
