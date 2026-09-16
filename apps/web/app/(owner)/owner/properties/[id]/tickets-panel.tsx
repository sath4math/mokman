"use client";

import Link from "next/link";
import { useState } from "react";

import type { MaintenanceTicket } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./tickets-panel.module.css";

const CATEGORIES = ["plumbing", "electrical", "appliance", "structural", "pest_control", "other"];
const PRIORITIES = ["low", "medium", "high", "urgent"] as const;

export function TicketsPanel({
  propertyId,
  initialTickets,
}: {
  propertyId: string;
  initialTickets: MaintenanceTicket[];
}) {
  const [tickets, setTickets] = useState(initialTickets);
  const [draft, setDraft] = useState({ category: CATEGORIES[0], description: "", priority: "medium" as string });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleCreate() {
    if (!draft.description) return;
    setError(null);
    setBusy(true);
    try {
      const response = await fetch("/api/backend/maintenance/tickets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          property_id: propertyId,
          category: draft.category,
          description: draft.description,
          priority: draft.priority,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to raise ticket");
        return;
      }
      setTickets((prev) => [data, ...prev]);
      setDraft({ category: CATEGORIES[0], description: "", priority: "medium" });
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className={styles.section}>
      <h2 className={styles.heading}>Maintenance</h2>
      <ul className={styles.list}>
        {tickets.map((ticket) => (
          <li key={ticket.id}>
            <Link href={`/owner/tickets/${ticket.id}`} className={styles.item}>
              <div className={styles.itemInfo}>
                <span>
                  {ticket.category} — {ticket.description.slice(0, 60)}
                </span>
                <span className={ui.faintText}>priority: {ticket.priority}</span>
              </div>
              <span className={ui.flexRow}>
                {ticket.sla_breached_at && <span className={ui.badgeDanger}>SLA breached</span>}
                <span className={ui.badge}>{ticket.status.replace(/_/g, " ")}</span>
              </span>
            </Link>
          </li>
        ))}
        {tickets.length === 0 && <p className={ui.mutedText}>No maintenance tickets yet.</p>}
      </ul>

      <div className={styles.formRow}>
        <label className={ui.field}>
          Category
          <select
            className={ui.select}
            value={draft.category}
            onChange={(e) => setDraft((prev) => ({ ...prev, category: e.target.value }))}
          >
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>
        <label className={ui.field}>
          Priority
          <select
            className={ui.select}
            value={draft.priority}
            onChange={(e) => setDraft((prev) => ({ ...prev, priority: e.target.value }))}
          >
            {PRIORITIES.map((p) => (
              <option key={p} value={p}>
                {p}
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
        <button type="button" onClick={handleCreate} disabled={busy} className={ui.btnPrimary}>
          Raise ticket
        </button>
      </div>
      {error && <p className={ui.errorText}>{error}</p>}
    </section>
  );
}
