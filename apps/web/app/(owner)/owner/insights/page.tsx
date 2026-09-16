import { redirect } from "next/navigation";

import { LogoutButton } from "@/components/logout-button";
import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { ExpenseAnomaly, PropertyProfitability } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./insights.module.css";

export default async function OwnerInsightsPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const [profitability, anomalies] = await Promise.all([
    backendFetch<PropertyProfitability[]>("/finance/profitability"),
    backendFetch<ExpenseAnomaly[]>("/finance/anomalies"),
  ]);

  return (
    <main className={styles.main}>
      <div className={ui.flexBetween}>
        <h1 className={styles.title}>Insights</h1>
        <LogoutButton />
      </div>

      <section className={styles.section}>
        <h2 className={ui.badge}>Profitability comparison (this month)</h2>
        <ul className={styles.list}>
          {(profitability ?? []).map((p) => (
            <li key={p.property_id} className={styles.item}>
              <span>{p.property_name}</span>
              <strong>{p.net_payable}</strong>
            </li>
          ))}
          {(!profitability || profitability.length === 0) && (
            <p className={ui.mutedText}>No properties with financial activity yet.</p>
          )}
        </ul>
      </section>

      <section className={styles.section}>
        <h2 className={ui.badge}>Expense anomalies</h2>
        <ul className={styles.list}>
          {(anomalies ?? []).map((a) => (
            <li key={a.expense_id} className={styles.item}>
              <div className={styles.itemInfo}>
                <span>
                  {a.category}: {a.amount}
                </span>
                <span className={ui.faintText}>{a.reason}</span>
              </div>
            </li>
          ))}
          {(!anomalies || anomalies.length === 0) && (
            <p className={ui.mutedText}>No expense anomalies detected.</p>
          )}
        </ul>
      </section>
    </main>
  );
}
