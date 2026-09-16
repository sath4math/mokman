"use client";

import { useEffect, useState } from "react";

import type { EligibilityOutcome, OwnerPackage, ServiceCategory, ServiceEligibilityRule } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./eligibility-rules.module.css";

const PACKAGE_LABELS: Record<OwnerPackage, string> = {
  starter: "Starter",
  managed: "Managed",
  full_care: "Full Care",
  complete: "Complete",
};

const OUTCOME_LABELS: Record<EligibilityOutcome, string> = {
  included: "Included",
  chargeable: "Chargeable",
  third_party: "Third party required",
  out_of_scope: "Out of scope",
  escalate: "Escalate (owner approval required)",
};

export function AdminEligibilityRulesPanel({ categories }: { categories: ServiceCategory[] }) {
  const [categoryId, setCategoryId] = useState(categories[0]?.id ?? "");
  const [rules, setRules] = useState<ServiceEligibilityRule[]>([]);
  const [draft, setDraft] = useState<{
    package: OwnerPackage;
    outcome: EligibilityOutcome;
    notes: string;
    maxOccurrences: string;
    periodDays: string;
    maxValue: string;
  }>({
    package: "starter",
    outcome: "included",
    notes: "",
    maxOccurrences: "",
    periodDays: "",
    maxValue: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!categoryId) return;
    let cancelled = false;
    fetch(`/api/backend/maintenance/eligibility-rules?service_category_id=${categoryId}`)
      .then((response) => response.json())
      .then((data) => {
        if (!cancelled) setRules(Array.isArray(data) ? data : []);
      });
    return () => {
      cancelled = true;
    };
  }, [categoryId]);

  async function handleAdd() {
    if (!categoryId) return;
    setError(null);
    setBusy(true);
    try {
      const response = await fetch("/api/backend/maintenance/eligibility-rules", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          service_category_id: categoryId,
          package: draft.package,
          outcome: draft.outcome,
          notes: draft.notes || null,
          max_occurrences: draft.maxOccurrences ? Number(draft.maxOccurrences) : null,
          period_days: draft.periodDays ? Number(draft.periodDays) : null,
          max_value: draft.maxValue ? Number(draft.maxValue) : null,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to add eligibility rule");
        return;
      }
      setRules((prev) => [data, ...prev]);
      setDraft({
        package: "starter",
        outcome: "included",
        notes: "",
        maxOccurrences: "",
        periodDays: "",
        maxValue: "",
      });
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete(rule: ServiceEligibilityRule) {
    setError(null);
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/maintenance/eligibility-rules/${rule.id}`, {
        method: "DELETE",
      });
      if (!response.ok) {
        const data = await response.json().catch(() => null);
        setError(data?.detail ?? "Failed to delete eligibility rule");
        return;
      }
      setRules((prev) => prev.filter((r) => r.id !== rule.id));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <section className={styles.section}>
        <label className={ui.field}>
          Service category
          <select className={ui.select} value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </label>
      </section>

      {categoryId && (
        <>
          <section className={styles.section}>
            <h2 className={ui.badge}>Add a rule</h2>
            <div className={styles.formRow}>
              <label className={ui.field}>
                Owner package
                <select
                  className={ui.select}
                  value={draft.package}
                  onChange={(e) => setDraft((prev) => ({ ...prev, package: e.target.value as OwnerPackage }))}
                >
                  {Object.entries(PACKAGE_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </label>
              <label className={ui.field}>
                Outcome
                <select
                  className={ui.select}
                  value={draft.outcome}
                  onChange={(e) => setDraft((prev) => ({ ...prev, outcome: e.target.value as EligibilityOutcome }))}
                >
                  {Object.entries(OUTCOME_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </label>
              <label className={ui.field}>
                Notes
                <input
                  className={ui.input}
                  value={draft.notes}
                  onChange={(e) => setDraft((prev) => ({ ...prev, notes: e.target.value }))}
                />
              </label>
              <label className={ui.field}>
                Max occurrences (fair use)
                <input
                  type="number"
                  className={ui.input}
                  placeholder="e.g. 2"
                  value={draft.maxOccurrences}
                  onChange={(e) => setDraft((prev) => ({ ...prev, maxOccurrences: e.target.value }))}
                />
              </label>
              <label className={ui.field}>
                Per how many days
                <input
                  type="number"
                  className={ui.input}
                  placeholder="e.g. 90"
                  value={draft.periodDays}
                  onChange={(e) => setDraft((prev) => ({ ...prev, periodDays: e.target.value }))}
                />
              </label>
              <label className={ui.field}>
                Max value (fair use)
                <input
                  type="number"
                  className={ui.input}
                  placeholder="e.g. 500"
                  value={draft.maxValue}
                  onChange={(e) => setDraft((prev) => ({ ...prev, maxValue: e.target.value }))}
                />
              </label>
              <button type="button" onClick={handleAdd} disabled={busy} className={ui.btnPrimary}>
                Add rule
              </button>
            </div>
            {error && <p className={ui.errorText}>{error}</p>}
          </section>

          <section className={styles.section}>
            <h2 className={ui.badge}>Rules for this category</h2>
            <ul className={styles.list}>
              {rules.map((rule) => (
                <li key={rule.id} className={styles.item}>
                  <div className={styles.itemInfo}>
                    <span>
                      {PACKAGE_LABELS[rule.package]} → {OUTCOME_LABELS[rule.outcome]}
                    </span>
                    {(rule.max_occurrences != null || rule.max_value != null) && (
                      <span className={ui.faintText}>
                        Fair use:{" "}
                        {rule.max_occurrences != null &&
                          `≤${rule.max_occurrences} per ${rule.period_days} days`}
                        {rule.max_occurrences != null && rule.max_value != null && ", "}
                        {rule.max_value != null && `cap ${rule.max_value}`}
                      </span>
                    )}
                    {rule.notes && <span className={ui.faintText}>{rule.notes}</span>}
                  </div>
                  <button
                    type="button"
                    onClick={() => handleDelete(rule)}
                    disabled={busy}
                    className={ui.btnSecondary}
                  >
                    Delete
                  </button>
                </li>
              ))}
              {rules.length === 0 && <p className={ui.mutedText}>No eligibility rules for this category yet.</p>}
            </ul>
          </section>
        </>
      )}
    </>
  );
}
