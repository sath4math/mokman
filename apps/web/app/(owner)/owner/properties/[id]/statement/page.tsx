import { notFound } from "next/navigation";

import { backendFetch } from "@/lib/backend";
import { requireVerifiedOwner } from "@/lib/current-user";
import type { Property, PropertyStatement } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import { MonthPicker } from "./month-picker";
import styles from "./statement.module.css";

function currentMonth(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
}

export default async function PropertyStatementPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ month?: string }>;
}) {
  await requireVerifiedOwner();

  const { id } = await params;
  const { month: monthParam } = await searchParams;
  const month = monthParam ?? currentMonth();

  const [property, statement] = await Promise.all([
    backendFetch<Property>(`/properties/${id}`),
    backendFetch<PropertyStatement>(`/finance/statement?property_id=${id}&month=${month}`),
  ]);

  if (!property) notFound();

  return (
    <main className={styles.main}>
      <h1 className={styles.title}>{property.name} — Statement</h1>
      <MonthPicker propertyId={property.id} month={month} />

      {statement ? (
        <>
          <div className={styles.summaryGrid}>
            <div>
              <div className={ui.faintText}>Rent collected</div>
              <div>{statement.rent_collected}</div>
            </div>
            <div>
              <div className={ui.faintText}>Expenses</div>
              <div>{statement.expenses}</div>
            </div>
            <div>
              <div className={ui.faintText}>Mokman fee</div>
              <div>{statement.mokman_fee}</div>
            </div>
            <div>
              <div className={ui.faintText}>Net payable</div>
              <div>{statement.net_payable}</div>
            </div>
          </div>

          <div className={styles.entryTable}>
            {statement.entries.map((entry) => (
              <div key={entry.id} className={styles.entryRow}>
                <span>
                  {entry.entry_type.replace(/_/g, " ")}
                  {entry.reference_note ? ` — ${entry.reference_note}` : ""}
                </span>
                <span className={ui.faintText}>{new Date(entry.occurred_at).toLocaleDateString()}</span>
                <span>{entry.amount}</span>
              </div>
            ))}
            {statement.entries.length === 0 && (
              <p className={ui.mutedText}>No ledger activity for this month.</p>
            )}
          </div>
        </>
      ) : (
        <p className={ui.mutedText}>No financial activity for this month.</p>
      )}
    </main>
  );
}
