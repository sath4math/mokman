"use client";

import { useState } from "react";

import type { Expense, Property, Vendor } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./expenses.module.css";

export function AdminExpensesPanel({
  properties,
  initialExpenses,
  vendors,
}: {
  properties: Property[];
  initialExpenses: Expense[];
  vendors: Vendor[];
}) {
  const [expenses, setExpenses] = useState(initialExpenses);
  const [draft, setDraft] = useState({
    property_id: properties[0]?.id ?? "",
    category: "",
    amount: "",
    description: "",
    vendor_id: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const propertyName = (id: string) => properties.find((p) => p.id === id)?.name ?? id;
  const vendorName = (id: string) => vendors.find((v) => v.id === id)?.name ?? id;

  async function handleAdd() {
    if (!draft.property_id || !draft.category || !draft.amount) return;
    setError(null);
    setBusy(true);
    try {
      const response = await fetch("/api/backend/expenses", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          property_id: draft.property_id,
          category: draft.category,
          amount: Number(draft.amount),
          description: draft.description || null,
          vendor_id: draft.vendor_id || null,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to log expense");
        return;
      }
      setExpenses((prev) => [data, ...prev]);
      setDraft((prev) => ({ ...prev, category: "", amount: "", description: "", vendor_id: "" }));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <section className={styles.section}>
        <h2 className={ui.badge}>Log an expense</h2>
        <div className={styles.formRow}>
          <label className={ui.field}>
            Property
            <select
              className={ui.select}
              value={draft.property_id}
              onChange={(e) => setDraft((prev) => ({ ...prev, property_id: e.target.value }))}
            >
              {properties.map((property) => (
                <option key={property.id} value={property.id}>
                  {property.name}
                </option>
              ))}
            </select>
          </label>
          <label className={ui.field}>
            Category
            <input
              className={ui.input}
              placeholder="plumbing, pest control..."
              value={draft.category}
              onChange={(e) => setDraft((prev) => ({ ...prev, category: e.target.value }))}
            />
          </label>
          <label className={ui.field}>
            Amount
            <input
              type="number"
              className={ui.input}
              value={draft.amount}
              onChange={(e) => setDraft((prev) => ({ ...prev, amount: e.target.value }))}
            />
          </label>
          <label className={ui.field}>
            Description
            <input
              className={ui.input}
              value={draft.description}
              onChange={(e) => setDraft((prev) => ({ ...prev, description: e.target.value }))}
            />
          </label>
          <label className={ui.field}>
            Vendor (optional)
            <select
              className={ui.select}
              value={draft.vendor_id}
              onChange={(e) => setDraft((prev) => ({ ...prev, vendor_id: e.target.value }))}
            >
              <option value="">None</option>
              {vendors.map((vendor) => (
                <option key={vendor.id} value={vendor.id}>
                  {vendor.name}
                </option>
              ))}
            </select>
          </label>
          <button type="button" onClick={handleAdd} disabled={busy} className={ui.btnPrimary}>
            Submit for approval
          </button>
        </div>
        {error && <p className={ui.errorText}>{error}</p>}
      </section>

      <section className={styles.section}>
        <h2 className={ui.badge}>All expenses</h2>
        <ul className={styles.list}>
          {expenses.map((expense) => (
            <li key={expense.id} className={styles.item}>
              <span>
                {propertyName(expense.property_id)} — {expense.category} — {expense.amount}
                {expense.vendor_id ? ` — ${vendorName(expense.vendor_id)}` : ""}
              </span>
              <span className={ui.badge}>{expense.status}</span>
            </li>
          ))}
          {expenses.length === 0 && <p className={ui.mutedText}>No expenses yet.</p>}
        </ul>
      </section>
    </>
  );
}
