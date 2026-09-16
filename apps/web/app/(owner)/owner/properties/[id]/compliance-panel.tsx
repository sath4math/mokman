"use client";

import { useState } from "react";

import type { ComplianceCategory, ComplianceDue } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./compliance-panel.module.css";

const CATEGORIES: ComplianceCategory[] = ["society_maintenance", "property_tax", "other"];

export function CompliancePanel({
  propertyId,
  initialDues,
}: {
  propertyId: string;
  initialDues: ComplianceDue[];
}) {
  const [dues, setDues] = useState(initialDues);
  const [draft, setDraft] = useState({
    category: CATEGORIES[0],
    description: "",
    amount: "",
    due_date: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleCreate() {
    if (!draft.amount || !draft.due_date) return;
    setError(null);
    setBusy(true);
    try {
      const response = await fetch("/api/backend/compliance/dues", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          property_id: propertyId,
          category: draft.category,
          description: draft.description || null,
          amount: Number(draft.amount),
          due_date: draft.due_date,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to add due");
        return;
      }
      setDues((prev) => [...prev, data]);
      setDraft({ category: CATEGORIES[0], description: "", amount: "", due_date: "" });
    } finally {
      setBusy(false);
    }
  }

  async function handleMarkPaid(dueId: string) {
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/compliance/dues/${dueId}/mark-paid`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      const data = await response.json();
      if (response.ok) {
        setDues((prev) => prev.map((d) => (d.id === dueId ? data : d)));
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className={styles.section}>
      <h2 className={styles.heading}>Society &amp; government dues</h2>
      <ul className={styles.list}>
        {dues.map((due) => (
          <li key={due.id} className={styles.item}>
            <div className={styles.itemInfo}>
              <span>
                {due.category.replace(/_/g, " ")} — {due.amount} — due {due.due_date}
              </span>
              {due.description && <span className={ui.faintText}>{due.description}</span>}
            </div>
            {due.paid_at ? (
              <span className={ui.badge}>paid</span>
            ) : (
              <button
                type="button"
                onClick={() => handleMarkPaid(due.id)}
                disabled={busy}
                className={`${ui.btnSecondary} ${ui.btnSmall}`}
              >
                Mark paid
              </button>
            )}
          </li>
        ))}
        {dues.length === 0 && <p className={ui.mutedText}>No dues recorded yet.</p>}
      </ul>

      <div className={styles.formRow}>
        <label className={ui.field}>
          Category
          <select
            className={ui.select}
            value={draft.category}
            onChange={(e) => setDraft((prev) => ({ ...prev, category: e.target.value as ComplianceCategory }))}
          >
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c.replace(/_/g, " ")}
              </option>
            ))}
          </select>
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
          Amount
          <input
            type="number"
            className={ui.input}
            value={draft.amount}
            onChange={(e) => setDraft((prev) => ({ ...prev, amount: e.target.value }))}
          />
        </label>
        <label className={ui.field}>
          Due date
          <input
            type="date"
            className={ui.input}
            value={draft.due_date}
            onChange={(e) => setDraft((prev) => ({ ...prev, due_date: e.target.value }))}
          />
        </label>
        <button type="button" onClick={handleCreate} disabled={busy} className={ui.btnPrimary}>
          Add due
        </button>
      </div>
      {error && <p className={ui.errorText}>{error}</p>}
    </section>
  );
}
