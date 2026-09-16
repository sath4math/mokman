"use client";

import { useState } from "react";

import type { Vendor } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./vendors.module.css";

export function AdminVendorsPanel({ initialVendors }: { initialVendors: Vendor[] }) {
  const [vendors, setVendors] = useState(initialVendors);
  const [draft, setDraft] = useState({ name: "", service_category: "", phone: "", email: "" });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleAdd() {
    if (!draft.name || !draft.service_category) return;
    setError(null);
    setBusy(true);
    try {
      const response = await fetch("/api/backend/vendors", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: draft.name,
          service_category: draft.service_category,
          phone: draft.phone || null,
          email: draft.email || null,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to add vendor");
        return;
      }
      setVendors((prev) => [data, ...prev]);
      setDraft({ name: "", service_category: "", phone: "", email: "" });
    } finally {
      setBusy(false);
    }
  }

  async function toggleActive(vendor: Vendor) {
    setError(null);
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/vendors/${vendor.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_active: !vendor.is_active }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to update vendor");
        return;
      }
      setVendors((prev) => prev.map((v) => (v.id === vendor.id ? data : v)));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <section className={styles.section}>
        <h2 className={ui.badge}>Add a vendor</h2>
        <div className={styles.formRow}>
          <label className={ui.field}>
            Name
            <input
              className={ui.input}
              value={draft.name}
              onChange={(e) => setDraft((prev) => ({ ...prev, name: e.target.value }))}
            />
          </label>
          <label className={ui.field}>
            Service category
            <input
              className={ui.input}
              placeholder="plumbing, electrical..."
              value={draft.service_category}
              onChange={(e) => setDraft((prev) => ({ ...prev, service_category: e.target.value }))}
            />
          </label>
          <label className={ui.field}>
            Phone
            <input
              className={ui.input}
              value={draft.phone}
              onChange={(e) => setDraft((prev) => ({ ...prev, phone: e.target.value }))}
            />
          </label>
          <label className={ui.field}>
            Email
            <input
              className={ui.input}
              value={draft.email}
              onChange={(e) => setDraft((prev) => ({ ...prev, email: e.target.value }))}
            />
          </label>
          <button type="button" onClick={handleAdd} disabled={busy} className={ui.btnPrimary}>
            Add vendor
          </button>
        </div>
        {error && <p className={ui.errorText}>{error}</p>}
      </section>

      <section className={styles.section}>
        <h2 className={ui.badge}>Vendor directory</h2>
        <ul className={styles.list}>
          {vendors.map((vendor) => (
            <li key={vendor.id} className={styles.item}>
              <span>
                {vendor.name} — {vendor.service_category}
                {vendor.phone ? ` — ${vendor.phone}` : ""}
              </span>
              <span className={ui.flexRow}>
                <span className={ui.badge}>{vendor.is_active ? "active" : "inactive"}</span>
                <button
                  type="button"
                  onClick={() => toggleActive(vendor)}
                  disabled={busy}
                  className={ui.btnSecondary}
                >
                  {vendor.is_active ? "Deactivate" : "Activate"}
                </button>
              </span>
            </li>
          ))}
          {vendors.length === 0 && <p className={ui.mutedText}>No vendors yet.</p>}
        </ul>
      </section>
    </>
  );
}
