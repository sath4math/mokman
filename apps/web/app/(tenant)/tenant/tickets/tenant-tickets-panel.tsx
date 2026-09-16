"use client";

import Link from "next/link";
import { useState } from "react";

import type { MaintenanceTicket, ServiceCategory } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./tickets.module.css";

const FALLBACK_CATEGORIES = ["plumbing", "electrical", "appliance", "structural", "pest_control", "other"];
const PRIORITIES = ["low", "medium", "high", "urgent"] as const;

export function TenantTicketsPanel({
  properties,
  initialTickets,
  serviceCategories,
}: {
  properties: { id: string; label: string }[];
  initialTickets: MaintenanceTicket[];
  serviceCategories: ServiceCategory[];
}) {
  const [tickets, setTickets] = useState(initialTickets);
  const categoryOptions =
    serviceCategories.length > 0
      ? [...new Set([...serviceCategories.map((c) => c.name), "other"])]
      : FALLBACK_CATEGORIES;
  const [draft, setDraft] = useState({
    property_id: properties[0]?.id ?? "",
    category: categoryOptions[0],
    description: "",
    priority: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleCreate() {
    if (!draft.property_id || !draft.description) return;
    setError(null);
    setBusy(true);
    try {
      const response = await fetch("/api/backend/maintenance/tickets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          property_id: draft.property_id,
          category: draft.category,
          description: draft.description,
          ...(draft.priority ? { priority: draft.priority } : {}),
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to raise ticket");
        return;
      }
      setTickets((prev) => [data, ...prev]);
      setDraft((prev) => ({ ...prev, description: "" }));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <section className={styles.section}>
        <h2 className={ui.badge}>Raise a ticket</h2>
        <div className={styles.formRow}>
          <label className={ui.field}>
            Property
            <select
              className={ui.select}
              value={draft.property_id}
              onChange={(e) => setDraft((prev) => ({ ...prev, property_id: e.target.value }))}
            >
              {properties.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.label}
                </option>
              ))}
            </select>
          </label>
          <label className={ui.field}>
            Category
            <select
              className={ui.select}
              value={draft.category}
              onChange={(e) => setDraft((prev) => ({ ...prev, category: e.target.value }))}
            >
              {categoryOptions.map((c) => (
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
              <option value="">Auto (based on category)</option>
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
          <button type="button" onClick={handleCreate} disabled={busy || !draft.property_id} className={ui.btnPrimary}>
            Raise ticket
          </button>
        </div>
        {error && <p className={ui.errorText}>{error}</p>}
      </section>

      <section className={styles.section}>
        <h2 className={ui.badge}>Your tickets</h2>
        <ul className={styles.list}>
          {tickets.map((ticket) => (
            <li key={ticket.id}>
              <Link href={`/tenant/tickets/${ticket.id}`} className={styles.item}>
                <div className={styles.itemInfo}>
                  <span>
                    {ticket.category} — {ticket.description.slice(0, 60)}
                  </span>
                  <span className={ui.faintText}>priority: {ticket.priority}</span>
                </div>
                <span className={ui.badge}>{ticket.status.replace(/_/g, " ")}</span>
              </Link>
            </li>
          ))}
          {tickets.length === 0 && <p className={ui.mutedText}>No tickets raised yet.</p>}
        </ul>
      </section>
    </>
  );
}
