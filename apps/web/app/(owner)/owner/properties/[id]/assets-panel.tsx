"use client";

import { useState } from "react";

import type { Asset } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./assets-panel.module.css";

export function AssetsPanel({ propertyId, initialAssets }: { propertyId: string; initialAssets: Asset[] }) {
  const [assets, setAssets] = useState(initialAssets);
  const [draft, setDraft] = useState({
    category: "",
    name: "",
    purchase_date: "",
    purchase_cost: "",
    useful_life_years: "",
    warranty_expires_on: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleCreate() {
    if (!draft.category.trim() || !draft.name.trim()) return;
    setError(null);
    setBusy(true);
    try {
      const response = await fetch("/api/backend/assets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          property_id: propertyId,
          category: draft.category,
          name: draft.name,
          purchase_date: draft.purchase_date || null,
          purchase_cost: draft.purchase_cost ? Number(draft.purchase_cost) : null,
          useful_life_years: draft.useful_life_years ? Number(draft.useful_life_years) : null,
          warranty_expires_on: draft.warranty_expires_on || null,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to add asset");
        return;
      }
      setAssets((prev) => [...prev, data]);
      setDraft({
        category: "",
        name: "",
        purchase_date: "",
        purchase_cost: "",
        useful_life_years: "",
        warranty_expires_on: "",
      });
    } finally {
      setBusy(false);
    }
  }

  async function handleDispose(assetId: string) {
    const reason = window.prompt("Reason for disposal?");
    if (!reason) return;
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/assets/${assetId}/dispose`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason }),
      });
      const data = await response.json();
      if (response.ok) {
        setAssets((prev) => prev.map((a) => (a.id === assetId ? data : a)));
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className={styles.section}>
      <h2 className={styles.heading}>Assets</h2>
      <ul className={styles.list}>
        {assets.map((asset) => (
          <li key={asset.id} className={styles.item}>
            <div className={styles.itemInfo}>
              <span>
                {asset.name} ({asset.category})
                {asset.current_value != null ? ` — current value ${asset.current_value.toFixed(2)}` : ""}
              </span>
              {asset.warranty_expires_on && (
                <span className={ui.faintText}>Warranty until {asset.warranty_expires_on}</span>
              )}
            </div>
            {asset.is_active ? (
              <button
                type="button"
                onClick={() => handleDispose(asset.id)}
                disabled={busy}
                className={`${ui.btnSecondary} ${ui.btnSmall}`}
              >
                Dispose
              </button>
            ) : (
              <span className={ui.badge}>{asset.disposed_reason ?? "disposed"}</span>
            )}
          </li>
        ))}
        {assets.length === 0 && <p className={ui.mutedText}>No assets recorded yet.</p>}
      </ul>

      <div className={styles.formRow}>
        <label className={ui.field}>
          Category
          <input
            className={ui.input}
            placeholder="appliance, furniture..."
            value={draft.category}
            onChange={(e) => setDraft((prev) => ({ ...prev, category: e.target.value }))}
          />
        </label>
        <label className={ui.field}>
          Name
          <input
            className={ui.input}
            value={draft.name}
            onChange={(e) => setDraft((prev) => ({ ...prev, name: e.target.value }))}
          />
        </label>
        <label className={ui.field}>
          Purchase date
          <input
            type="date"
            className={ui.input}
            value={draft.purchase_date}
            onChange={(e) => setDraft((prev) => ({ ...prev, purchase_date: e.target.value }))}
          />
        </label>
        <label className={ui.field}>
          Purchase cost
          <input
            type="number"
            className={ui.input}
            value={draft.purchase_cost}
            onChange={(e) => setDraft((prev) => ({ ...prev, purchase_cost: e.target.value }))}
          />
        </label>
        <label className={ui.field}>
          Useful life (years)
          <input
            type="number"
            className={ui.input}
            value={draft.useful_life_years}
            onChange={(e) => setDraft((prev) => ({ ...prev, useful_life_years: e.target.value }))}
          />
        </label>
        <label className={ui.field}>
          Warranty until
          <input
            type="date"
            className={ui.input}
            value={draft.warranty_expires_on}
            onChange={(e) => setDraft((prev) => ({ ...prev, warranty_expires_on: e.target.value }))}
          />
        </label>
        <button type="button" onClick={handleCreate} disabled={busy} className={ui.btnPrimary}>
          Add asset
        </button>
      </div>
      {error && <p className={ui.errorText}>{error}</p>}
    </section>
  );
}
