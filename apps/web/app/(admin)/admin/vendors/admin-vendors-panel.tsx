"use client";

import { useState } from "react";

import type { Vendor, VendorRateCard } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./vendors.module.css";

export function AdminVendorsPanel({ initialVendors }: { initialVendors: Vendor[] }) {
  const [vendors, setVendors] = useState(initialVendors);
  const [draft, setDraft] = useState({ name: "", service_category: "", phone: "", email: "" });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const [expanded, setExpanded] = useState<string | null>(null);
  const [rateCards, setRateCards] = useState<Record<string, VendorRateCard[]>>({});
  const [rateCardDraft, setRateCardDraft] = useState({ service_category: "", unit: "", rate: "" });

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

  async function handleBlacklist(vendor: Vendor) {
    const reason = window.prompt(`Reason for blacklisting ${vendor.name}?`);
    if (!reason) return;
    setError(null);
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/vendors/${vendor.id}/blacklist`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to blacklist vendor");
        return;
      }
      setVendors((prev) => prev.map((v) => (v.id === vendor.id ? data : v)));
    } finally {
      setBusy(false);
    }
  }

  async function handleReinstate(vendor: Vendor) {
    setError(null);
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/vendors/${vendor.id}/reinstate`, { method: "POST" });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to reinstate vendor");
        return;
      }
      setVendors((prev) => prev.map((v) => (v.id === vendor.id ? data : v)));
    } finally {
      setBusy(false);
    }
  }

  async function toggleRateCards(vendorId: string) {
    if (expanded === vendorId) {
      setExpanded(null);
      return;
    }
    setExpanded(vendorId);
    if (!rateCards[vendorId]) {
      const response = await fetch(`/api/backend/vendors/${vendorId}/rate-cards`);
      if (response.ok) {
        const data = await response.json();
        setRateCards((prev) => ({ ...prev, [vendorId]: data }));
      }
    }
  }

  async function handleAddRateCard(vendorId: string) {
    if (!rateCardDraft.service_category || !rateCardDraft.unit || !rateCardDraft.rate) return;
    setError(null);
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/vendors/${vendorId}/rate-cards`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          service_category: rateCardDraft.service_category,
          unit: rateCardDraft.unit,
          rate: Number(rateCardDraft.rate),
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to add rate card");
        return;
      }
      setRateCards((prev) => ({ ...prev, [vendorId]: [...(prev[vendorId] ?? []), data] }));
      setRateCardDraft({ service_category: "", unit: "", rate: "" });
    } finally {
      setBusy(false);
    }
  }

  async function handleDeleteRateCard(vendorId: string, rateCardId: string) {
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/vendors/${vendorId}/rate-cards/${rateCardId}`, {
        method: "DELETE",
      });
      if (response.ok) {
        setRateCards((prev) => ({
          ...prev,
          [vendorId]: (prev[vendorId] ?? []).filter((r) => r.id !== rateCardId),
        }));
      }
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
            <li key={vendor.id} className={styles.vendorBlock}>
              <div className={styles.item}>
                <span>
                  {vendor.name} — {vendor.service_category}
                  {vendor.phone ? ` — ${vendor.phone}` : ""}
                  {vendor.average_rating != null ? ` — ★${vendor.average_rating.toFixed(1)}` : ""}
                </span>
                <span className={ui.flexRow}>
                  <span className={ui.badge}>{vendor.is_active ? "active" : "blacklisted"}</span>
                  {vendor.is_active ? (
                    <button
                      type="button"
                      onClick={() => handleBlacklist(vendor)}
                      disabled={busy}
                      className={ui.btnSecondary}
                    >
                      Blacklist
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={() => handleReinstate(vendor)}
                      disabled={busy}
                      className={ui.btnSecondary}
                    >
                      Reinstate
                    </button>
                  )}
                  <button type="button" onClick={() => toggleRateCards(vendor.id)} className={ui.link}>
                    {expanded === vendor.id ? "Hide rate cards" : "Rate cards"}
                  </button>
                </span>
              </div>

              {expanded === vendor.id && (
                <div className={styles.rateCardsBlock}>
                  <ul className={styles.list}>
                    {(rateCards[vendor.id] ?? []).map((card) => (
                      <li key={card.id} className={styles.rateCardItem}>
                        <span>
                          {card.service_category} — {card.rate}/{card.unit}
                        </span>
                        <button
                          type="button"
                          onClick={() => handleDeleteRateCard(vendor.id, card.id)}
                          className={ui.linkDanger}
                        >
                          Remove
                        </button>
                      </li>
                    ))}
                    {(rateCards[vendor.id] ?? []).length === 0 && (
                      <p className={ui.mutedText}>No rate cards yet.</p>
                    )}
                  </ul>
                  <div className={styles.formRow}>
                    <label className={ui.field}>
                      Service category
                      <input
                        className={ui.input}
                        value={rateCardDraft.service_category}
                        onChange={(e) =>
                          setRateCardDraft((prev) => ({ ...prev, service_category: e.target.value }))
                        }
                      />
                    </label>
                    <label className={ui.field}>
                      Unit
                      <input
                        className={ui.input}
                        placeholder="per visit, per hour..."
                        value={rateCardDraft.unit}
                        onChange={(e) => setRateCardDraft((prev) => ({ ...prev, unit: e.target.value }))}
                      />
                    </label>
                    <label className={ui.field}>
                      Rate
                      <input
                        type="number"
                        className={ui.input}
                        value={rateCardDraft.rate}
                        onChange={(e) => setRateCardDraft((prev) => ({ ...prev, rate: e.target.value }))}
                      />
                    </label>
                    <button
                      type="button"
                      onClick={() => handleAddRateCard(vendor.id)}
                      disabled={busy}
                      className={`${ui.btnPrimary} ${ui.btnSmall}`}
                    >
                      Add rate card
                    </button>
                  </div>
                </div>
              )}
            </li>
          ))}
          {vendors.length === 0 && <p className={ui.mutedText}>No vendors yet.</p>}
        </ul>
      </section>
    </>
  );
}
