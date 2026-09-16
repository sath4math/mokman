"use client";

import { useState } from "react";

import type { ServiceCategory, TicketPriority } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./service-categories.module.css";

const PRIORITIES: TicketPriority[] = ["low", "medium", "high", "urgent"];

export function AdminServiceCategoriesPanel({
  initialCategories,
}: {
  initialCategories: ServiceCategory[];
}) {
  const [categories, setCategories] = useState(initialCategories);
  const [draft, setDraft] = useState({
    name: "",
    default_priority: "medium" as TicketPriority,
    estimated_completion_hours: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleAdd() {
    if (!draft.name) return;
    setError(null);
    setBusy(true);
    try {
      const response = await fetch("/api/backend/maintenance/service-categories", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: draft.name,
          default_priority: draft.default_priority,
          estimated_completion_hours: draft.estimated_completion_hours
            ? Number(draft.estimated_completion_hours)
            : null,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to add service category");
        return;
      }
      setCategories((prev) => [data, ...prev]);
      setDraft({ name: "", default_priority: "medium", estimated_completion_hours: "" });
    } finally {
      setBusy(false);
    }
  }

  async function toggleActive(category: ServiceCategory) {
    setError(null);
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/maintenance/service-categories/${category.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_active: !category.is_active }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to update service category");
        return;
      }
      setCategories((prev) => prev.map((c) => (c.id === category.id ? data : c)));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <section className={styles.section}>
        <h2 className={ui.badge}>Add a service category</h2>
        <div className={styles.formRow}>
          <label className={ui.field}>
            Name
            <input
              className={ui.input}
              placeholder="emergency_response, move_in_prep..."
              value={draft.name}
              onChange={(e) => setDraft((prev) => ({ ...prev, name: e.target.value }))}
            />
          </label>
          <label className={ui.field}>
            Default priority
            <select
              className={ui.select}
              value={draft.default_priority}
              onChange={(e) =>
                setDraft((prev) => ({ ...prev, default_priority: e.target.value as TicketPriority }))
              }
            >
              {PRIORITIES.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </label>
          <label className={ui.field}>
            Estimated completion (hours, optional)
            <input
              type="number"
              className={ui.input}
              value={draft.estimated_completion_hours}
              onChange={(e) => setDraft((prev) => ({ ...prev, estimated_completion_hours: e.target.value }))}
            />
          </label>
          <button type="button" onClick={handleAdd} disabled={busy} className={ui.btnPrimary}>
            Add category
          </button>
        </div>
        {error && <p className={ui.errorText}>{error}</p>}
      </section>

      <section className={styles.section}>
        <h2 className={ui.badge}>Service categories</h2>
        <ul className={styles.list}>
          {categories.map((category) => (
            <li key={category.id} className={styles.item}>
              <div className={styles.itemInfo}>
                <span>{category.name}</span>
                <span className={ui.faintText}>
                  default priority: {category.default_priority}
                  {category.estimated_completion_hours != null
                    ? ` — est. ${category.estimated_completion_hours}h`
                    : ""}
                </span>
              </div>
              <span className={ui.flexRow}>
                <span className={ui.badge}>{category.is_active ? "active" : "inactive"}</span>
                <button
                  type="button"
                  onClick={() => toggleActive(category)}
                  disabled={busy}
                  className={ui.btnSecondary}
                >
                  {category.is_active ? "Deactivate" : "Activate"}
                </button>
              </span>
            </li>
          ))}
          {categories.length === 0 && <p className={ui.mutedText}>No service categories yet.</p>}
        </ul>
      </section>
    </>
  );
}
