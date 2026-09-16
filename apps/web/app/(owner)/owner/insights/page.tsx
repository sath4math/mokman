import { redirect } from "next/navigation";

import { LogoutButton } from "@/components/logout-button";
import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type {
  ExpenseAnomaly,
  InvestmentSummary,
  PropertyProfitability,
  RecurringProblem,
  RentEscalationProjection,
} from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./insights.module.css";

function formatPercent(value: number | null): string {
  return value == null ? "—" : `${value.toFixed(1)}%`;
}

export default async function OwnerInsightsPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const [profitability, anomalies, recurringProblems, escalationProjections, investmentPortfolio] =
    await Promise.all([
      backendFetch<PropertyProfitability[]>("/finance/profitability"),
      backendFetch<ExpenseAnomaly[]>("/finance/anomalies"),
      backendFetch<RecurringProblem[]>("/maintenance/reports/recurring-problems"),
      backendFetch<RentEscalationProjection[]>("/rent/escalation-projections"),
      backendFetch<InvestmentSummary[]>("/properties/investment-portfolio"),
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

      <section className={styles.section}>
        <h2 className={ui.badge}>Recurring problems (last 180 days)</h2>
        <ul className={styles.list}>
          {(recurringProblems ?? []).map((r) => (
            <li key={`${r.property_id}-${r.category}`} className={styles.item}>
              <div className={styles.itemInfo}>
                <span>
                  {r.property_name}: {r.category}
                </span>
                <span className={ui.faintText}>
                  {r.ticket_count} tickets in the last {r.window_days} days
                </span>
              </div>
            </li>
          ))}
          {(!recurringProblems || recurringProblems.length === 0) && (
            <p className={ui.mutedText}>No recurring problems detected.</p>
          )}
        </ul>
      </section>

      <section className={styles.section}>
        <h2 className={ui.badge}>Rent escalation projections</h2>
        <ul className={styles.list}>
          {(escalationProjections ?? []).map((p) => (
            <li key={p.lease_id} className={styles.item}>
              <span>
                {p.current_rent} → {p.projected_rent}
              </span>
              <span className={ui.faintText}>from {p.escalation_date}</span>
            </li>
          ))}
          {(!escalationProjections || escalationProjections.length === 0) && (
            <p className={ui.mutedText}>No upcoming escalations on active leases.</p>
          )}
        </ul>
      </section>

      <section className={styles.section}>
        <h2 className={ui.badge}>Investment portfolio</h2>
        <ul className={styles.list}>
          {(investmentPortfolio ?? []).map((s) => (
            <li key={s.property_id} className={styles.item}>
              <div className={styles.itemInfo}>
                <span>{s.property_name}</span>
                <span className={ui.faintText}>
                  Yield {formatPercent(s.gross_yield_percentage)} · Appreciation{" "}
                  {formatPercent(s.appreciation_percentage)} · ROI {formatPercent(s.roi_percentage)}
                </span>
              </div>
            </li>
          ))}
          {(!investmentPortfolio || investmentPortfolio.length === 0) && (
            <p className={ui.mutedText}>No properties yet.</p>
          )}
        </ul>
      </section>
    </main>
  );
}
