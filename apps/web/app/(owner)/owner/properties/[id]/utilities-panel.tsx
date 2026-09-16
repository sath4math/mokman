"use client";

import { useState } from "react";

import type { UtilityBill, UtilityConnection, UtilityResponsibility } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./utilities-panel.module.css";

const UTILITY_TYPES = ["electricity", "water", "gas", "internet", "other"];

export function UtilitiesPanel({
  propertyId,
  initialConnections,
}: {
  propertyId: string;
  initialConnections: UtilityConnection[];
}) {
  const [connections, setConnections] = useState(initialConnections);
  const [bills, setBills] = useState<Record<string, UtilityBill[]>>({});
  const [expanded, setExpanded] = useState<string | null>(null);
  const [connectionDraft, setConnectionDraft] = useState({
    utility_type: UTILITY_TYPES[0],
    provider: "",
    account_number: "",
    responsibility: "owner" as UtilityResponsibility,
  });
  const [billDraft, setBillDraft] = useState({
    billing_period_start: "",
    billing_period_end: "",
    amount: "",
    due_date: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleAddConnection() {
    setError(null);
    setBusy(true);
    try {
      const response = await fetch("/api/backend/utilities/connections", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ property_id: propertyId, ...connectionDraft }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to add connection");
        return;
      }
      setConnections((prev) => [...prev, data]);
      setConnectionDraft({
        utility_type: UTILITY_TYPES[0],
        provider: "",
        account_number: "",
        responsibility: "owner",
      });
    } finally {
      setBusy(false);
    }
  }

  async function toggleBills(connectionId: string) {
    if (expanded === connectionId) {
      setExpanded(null);
      return;
    }
    setExpanded(connectionId);
    if (!bills[connectionId]) {
      const response = await fetch(`/api/backend/utilities/connections/${connectionId}/bills`);
      if (response.ok) {
        const data = await response.json();
        setBills((prev) => ({ ...prev, [connectionId]: data }));
      }
    }
  }

  async function handleAddBill(connectionId: string) {
    if (!billDraft.billing_period_start || !billDraft.billing_period_end || !billDraft.amount || !billDraft.due_date) {
      return;
    }
    setError(null);
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/utilities/connections/${connectionId}/bills`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          billing_period_start: billDraft.billing_period_start,
          billing_period_end: billDraft.billing_period_end,
          amount: Number(billDraft.amount),
          due_date: billDraft.due_date,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to add bill");
        return;
      }
      setBills((prev) => ({ ...prev, [connectionId]: [data, ...(prev[connectionId] ?? [])] }));
      setBillDraft({ billing_period_start: "", billing_period_end: "", amount: "", due_date: "" });
    } finally {
      setBusy(false);
    }
  }

  async function handleMarkPaid(connectionId: string, billId: string) {
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/utilities/bills/${billId}/mark-paid`, { method: "POST" });
      const data = await response.json();
      if (response.ok) {
        setBills((prev) => ({
          ...prev,
          [connectionId]: (prev[connectionId] ?? []).map((b) => (b.id === billId ? data : b)),
        }));
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className={styles.section}>
      <h2 className={styles.heading}>Utilities</h2>
      <ul className={styles.list}>
        {connections.map((connection) => (
          <li key={connection.id} className={styles.connectionBlock}>
            <button type="button" onClick={() => toggleBills(connection.id)} className={styles.item}>
              <span className={styles.itemInfo}>
                <span>
                  {connection.utility_type} {connection.provider ? `— ${connection.provider}` : ""}
                </span>
                <span className={ui.faintText}>responsibility: {connection.responsibility}</span>
              </span>
              <span className={ui.link}>{expanded === connection.id ? "Hide bills" : "View bills"}</span>
            </button>

            {expanded === connection.id && (
              <div className={styles.billsBlock}>
                <ul className={styles.list}>
                  {(bills[connection.id] ?? []).map((bill) => (
                    <li key={bill.id} className={styles.billItem}>
                      <span>
                        {bill.billing_period_start} → {bill.billing_period_end} — {bill.amount}
                      </span>
                      {bill.paid_at ? (
                        <span className={ui.badge}>paid</span>
                      ) : (
                        <button
                          type="button"
                          onClick={() => handleMarkPaid(connection.id, bill.id)}
                          disabled={busy}
                          className={`${ui.btnSecondary} ${ui.btnSmall}`}
                        >
                          Mark paid
                        </button>
                      )}
                    </li>
                  ))}
                  {(bills[connection.id] ?? []).length === 0 && <p className={ui.mutedText}>No bills yet.</p>}
                </ul>
                <div className={styles.formRow}>
                  <label className={ui.field}>
                    Period start
                    <input
                      type="date"
                      className={ui.input}
                      value={billDraft.billing_period_start}
                      onChange={(e) => setBillDraft((prev) => ({ ...prev, billing_period_start: e.target.value }))}
                    />
                  </label>
                  <label className={ui.field}>
                    Period end
                    <input
                      type="date"
                      className={ui.input}
                      value={billDraft.billing_period_end}
                      onChange={(e) => setBillDraft((prev) => ({ ...prev, billing_period_end: e.target.value }))}
                    />
                  </label>
                  <label className={ui.field}>
                    Amount
                    <input
                      type="number"
                      className={ui.input}
                      value={billDraft.amount}
                      onChange={(e) => setBillDraft((prev) => ({ ...prev, amount: e.target.value }))}
                    />
                  </label>
                  <label className={ui.field}>
                    Due date
                    <input
                      type="date"
                      className={ui.input}
                      value={billDraft.due_date}
                      onChange={(e) => setBillDraft((prev) => ({ ...prev, due_date: e.target.value }))}
                    />
                  </label>
                  <button
                    type="button"
                    onClick={() => handleAddBill(connection.id)}
                    disabled={busy}
                    className={`${ui.btnPrimary} ${ui.btnSmall}`}
                  >
                    Add bill
                  </button>
                </div>
              </div>
            )}
          </li>
        ))}
        {connections.length === 0 && <p className={ui.mutedText}>No utility connections yet.</p>}
      </ul>

      <div className={styles.formRow}>
        <label className={ui.field}>
          Type
          <select
            className={ui.select}
            value={connectionDraft.utility_type}
            onChange={(e) => setConnectionDraft((prev) => ({ ...prev, utility_type: e.target.value }))}
          >
            {UTILITY_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </label>
        <label className={ui.field}>
          Provider
          <input
            className={ui.input}
            value={connectionDraft.provider}
            onChange={(e) => setConnectionDraft((prev) => ({ ...prev, provider: e.target.value }))}
          />
        </label>
        <label className={ui.field}>
          Account number
          <input
            className={ui.input}
            value={connectionDraft.account_number}
            onChange={(e) => setConnectionDraft((prev) => ({ ...prev, account_number: e.target.value }))}
          />
        </label>
        <label className={ui.field}>
          Responsibility
          <select
            className={ui.select}
            value={connectionDraft.responsibility}
            onChange={(e) =>
              setConnectionDraft((prev) => ({ ...prev, responsibility: e.target.value as UtilityResponsibility }))
            }
          >
            <option value="owner">Owner</option>
            <option value="tenant">Tenant</option>
          </select>
        </label>
        <button type="button" onClick={handleAddConnection} disabled={busy} className={ui.btnPrimary}>
          Add connection
        </button>
      </div>
      {error && <p className={ui.errorText}>{error}</p>}
    </section>
  );
}
