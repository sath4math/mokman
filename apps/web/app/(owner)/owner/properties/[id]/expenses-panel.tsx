"use client";

import { useState } from "react";

import type { Expense } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./expenses-panel.module.css";

export function ExpensesPanel({
  propertyId,
  initialExpenses,
}: {
  propertyId: string;
  initialExpenses: Expense[];
}) {
  const [expenses, setExpenses] = useState(initialExpenses);
  const [draft, setDraft] = useState({ category: "", amount: "", description: "" });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleAdd() {
    if (!draft.category || !draft.amount) return;
    setError(null);
    setBusy(true);
    try {
      const response = await fetch("/api/backend/expenses", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          property_id: propertyId,
          category: draft.category,
          amount: Number(draft.amount),
          description: draft.description || null,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to log expense");
        return;
      }
      setExpenses((prev) => [data, ...prev]);
      setDraft({ category: "", amount: "", description: "" });
    } finally {
      setBusy(false);
    }
  }

  async function handleDecision(id: string, decision: "approve" | "reject") {
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/expenses/${id}/${decision}`, { method: "POST" });
      if (response.ok) {
        const updated = (await response.json()) as Expense;
        setExpenses((prev) => prev.map((e) => (e.id === updated.id ? updated : e)));
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className={styles.section}>
      <h2 className={styles.heading}>Expenses</h2>
      <ul className={styles.list}>
        {expenses.map((expense) => (
          <li key={expense.id} className={styles.item}>
            <div className={styles.itemInfo}>
              <span>
                {expense.category} — {expense.amount}
              </span>
              {expense.description && <span className={ui.faintText}>{expense.description}</span>}
            </div>
            <div className={styles.itemActions}>
              <span className={ui.badge}>{expense.status}</span>
              {expense.status === "pending" && (
                <>
                  <button
                    type="button"
                    onClick={() => handleDecision(expense.id, "approve")}
                    disabled={busy}
                    className={ui.linkPrimary}
                  >
                    Approve
                  </button>
                  <button
                    type="button"
                    onClick={() => handleDecision(expense.id, "reject")}
                    disabled={busy}
                    className={ui.linkDanger}
                  >
                    Reject
                  </button>
                </>
              )}
            </div>
          </li>
        ))}
        {expenses.length === 0 && <p className={ui.mutedText}>No expenses logged yet.</p>}
      </ul>

      <div className={styles.formRow}>
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
        <button type="button" onClick={handleAdd} disabled={busy} className={ui.btnPrimary}>
          Log expense
        </button>
      </div>
      {error && <p className={ui.errorText}>{error}</p>}
    </section>
  );
}
