"use client";

import { useState } from "react";

import type { ChecklistTemplate } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./checklist-templates.module.css";

export function AdminChecklistTemplatesPanel({
  initialTemplates,
}: {
  initialTemplates: ChecklistTemplate[];
}) {
  const [templates, setTemplates] = useState(initialTemplates);
  const [draft, setDraft] = useState({ category: "", items: "" });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleAdd() {
    const items = draft.items
      .split("\n")
      .map((item) => item.trim())
      .filter(Boolean);
    if (!draft.category || items.length === 0) return;
    setError(null);
    setBusy(true);
    try {
      const response = await fetch("/api/backend/maintenance/checklist-templates", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ category: draft.category, items }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to add checklist template");
        return;
      }
      setTemplates((prev) => [data, ...prev]);
      setDraft({ category: "", items: "" });
    } finally {
      setBusy(false);
    }
  }

  async function toggleActive(template: ChecklistTemplate) {
    setError(null);
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/maintenance/checklist-templates/${template.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_active: !template.is_active }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to update checklist template");
        return;
      }
      setTemplates((prev) => prev.map((t) => (t.id === template.id ? data : t)));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <section className={styles.section}>
        <h2 className={ui.badge}>Add a checklist template</h2>
        <div className={styles.formRow}>
          <label className={ui.field}>
            Category
            <input
              className={ui.input}
              placeholder="plumbing, electrical..."
              value={draft.category}
              onChange={(e) => setDraft((prev) => ({ ...prev, category: e.target.value }))}
            />
          </label>
          <label className={ui.field}>
            Items (one per line)
            <textarea
              className={ui.textarea}
              rows={4}
              value={draft.items}
              onChange={(e) => setDraft((prev) => ({ ...prev, items: e.target.value }))}
            />
          </label>
          <button type="button" onClick={handleAdd} disabled={busy} className={ui.btnPrimary}>
            Add template
          </button>
        </div>
        {error && <p className={ui.errorText}>{error}</p>}
      </section>

      <section className={styles.section}>
        <h2 className={ui.badge}>Checklist templates</h2>
        <ul className={styles.list}>
          {templates.map((template) => (
            <li key={template.id} className={styles.item}>
              <div className={styles.itemInfo}>
                <span>{template.category}</span>
                <span className={ui.faintText}>{template.items.join(" · ")}</span>
              </div>
              <span className={ui.flexRow}>
                <span className={ui.badge}>{template.is_active ? "active" : "inactive"}</span>
                <button
                  type="button"
                  onClick={() => toggleActive(template)}
                  disabled={busy}
                  className={ui.btnSecondary}
                >
                  {template.is_active ? "Deactivate" : "Activate"}
                </button>
              </span>
            </li>
          ))}
          {templates.length === 0 && <p className={ui.mutedText}>No checklist templates yet.</p>}
        </ul>
      </section>
    </>
  );
}
