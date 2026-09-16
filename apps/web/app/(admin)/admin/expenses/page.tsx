import { redirect } from "next/navigation";

import { LogoutButton } from "@/components/logout-button";
import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { Expense, Property, Vendor } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import { AdminExpensesPanel } from "./admin-expenses-panel";
import styles from "./expenses.module.css";

export default async function AdminExpensesPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const [properties, expenses, vendors] = await Promise.all([
    backendFetch<Property[]>("/properties"),
    backendFetch<Expense[]>("/expenses"),
    backendFetch<Vendor[]>("/vendors?active_only=true"),
  ]);

  return (
    <main className={styles.main}>
      <div className={ui.flexBetween}>
        <h1 className={styles.title}>Expenses</h1>
        <LogoutButton />
      </div>
      <AdminExpensesPanel properties={properties ?? []} initialExpenses={expenses ?? []} vendors={vendors ?? []} />
    </main>
  );
}
