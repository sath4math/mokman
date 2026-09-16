"use client";

import { useState } from "react";

import type { MaintenanceSchedule } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./preventive-maintenance-panel.module.css";

function isDue(nextDueOn: string): boolean {
  return new Date(nextDueOn) <= new Date();
}

export function PreventiveMaintenancePanel({
  propertyId,
  initialSchedules,
}: {
  propertyId: string;
  initialSchedules: MaintenanceSchedule[];
}) {
  const [schedules, setSchedules] = useState(initialSchedules);
  const [draft, setDraft] = useState({ category: "", frequency_days: "90", notes: "" });
  const [serviceDates, setServiceDates] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleCreate() {
    if (!draft.category || !draft.frequency_days) return;
    setError(null);
    setBusy(true);
    try {
      const response = await fetch("/api/backend/maintenance-schedules", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          property_id: propertyId,
          category: draft.category,
          frequency_days: Number(draft.frequency_days),
          notes: draft.notes || null,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to add schedule");
        return;
      }
      setSchedules((prev) => [...prev, data]);
      setDraft({ category: "", frequency_days: "90", notes: "" });
    } finally {
      setBusy(false);
    }
  }

  async function handleLogService(scheduleId: string) {
    const servicedOn = serviceDates[scheduleId];
    if (!servicedOn) return;
    setError(null);
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/maintenance-schedules/${scheduleId}/log-service`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ serviced_on: servicedOn }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to log service");
        return;
      }
      setSchedules((prev) => prev.map((s) => (s.id === scheduleId ? data : s)));
      setServiceDates((prev) => ({ ...prev, [scheduleId]: "" }));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className={styles.section}>
      <h2 className={styles.heading}>Preventive maintenance</h2>
      <ul className={styles.list}>
        {schedules.map((schedule) => (
          <li key={schedule.id} className={styles.item}>
            <div className={styles.itemInfo}>
              <span>
                {schedule.category} — every {schedule.frequency_days} days
              </span>
              <span className={ui.faintText}>
                last serviced: {schedule.last_serviced_on ?? "never"} · next due: {schedule.next_due_on}
              </span>
            </div>
            <div className={styles.logRow}>
              {isDue(schedule.next_due_on) && <span className={ui.badge}>due</span>}
              <input
                type="date"
                className={ui.input}
                value={serviceDates[schedule.id] ?? ""}
                onChange={(e) => setServiceDates((prev) => ({ ...prev, [schedule.id]: e.target.value }))}
              />
              <button
                type="button"
                onClick={() => handleLogService(schedule.id)}
                disabled={busy}
                className={`${ui.btnSecondary} ${ui.btnSmall}`}
              >
                Log service
              </button>
            </div>
          </li>
        ))}
        {schedules.length === 0 && <p className={ui.mutedText}>No preventive maintenance schedules yet.</p>}
      </ul>

      <div className={styles.formRow}>
        <label className={ui.field}>
          Category
          <input
            className={ui.input}
            placeholder="AC servicing, pest control..."
            value={draft.category}
            onChange={(e) => setDraft((prev) => ({ ...prev, category: e.target.value }))}
          />
        </label>
        <label className={ui.field}>
          Frequency (days)
          <input
            type="number"
            className={ui.input}
            value={draft.frequency_days}
            onChange={(e) => setDraft((prev) => ({ ...prev, frequency_days: e.target.value }))}
          />
        </label>
        <label className={ui.field}>
          Notes
          <input
            className={ui.input}
            value={draft.notes}
            onChange={(e) => setDraft((prev) => ({ ...prev, notes: e.target.value }))}
          />
        </label>
        <button type="button" onClick={handleCreate} disabled={busy} className={ui.btnPrimary}>
          Add schedule
        </button>
      </div>
      {error && <p className={ui.errorText}>{error}</p>}
    </section>
  );
}
