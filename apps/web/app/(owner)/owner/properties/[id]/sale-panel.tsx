"use client";

import { useState } from "react";

import type { PropertySale, SaleReadiness } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./sale-panel.module.css";

export function SalePanel({
  propertyId,
  initialSales,
  initialReadiness,
}: {
  propertyId: string;
  initialSales: PropertySale[];
  initialReadiness: SaleReadiness | null;
}) {
  const [sales, setSales] = useState(initialSales);
  const [readiness] = useState(initialReadiness);
  const [draft, setDraft] = useState({ listing_price: "", buyer_name: "", buyer_contact: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleCreate() {
    setError(null);
    setBusy(true);
    try {
      const response = await fetch("/api/backend/sales", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          property_id: propertyId,
          listing_price: draft.listing_price ? Number(draft.listing_price) : null,
          buyer_name: draft.buyer_name || null,
          buyer_contact: draft.buyer_contact || null,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to create sale record");
        return;
      }
      setSales((prev) => [...prev, data]);
      setDraft({ listing_price: "", buyer_name: "", buyer_contact: "" });
    } finally {
      setBusy(false);
    }
  }

  async function handleToggleTransfer(sale: PropertySale, field: keyof PropertySale) {
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/sales/${sale.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ [field]: !sale[field] }),
      });
      const data = await response.json();
      if (response.ok) {
        setSales((prev) => prev.map((s) => (s.id === sale.id ? data : s)));
      }
    } finally {
      setBusy(false);
    }
  }

  async function handleComplete(saleId: string) {
    const priceInput = window.prompt("Final sale price?");
    if (!priceInput) return;
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/sales/${saleId}/complete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sale_price: Number(priceInput) }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to complete sale");
        return;
      }
      setSales((prev) => prev.map((s) => (s.id === saleId ? data : s)));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className={styles.section}>
      <h2 className={styles.heading}>Sale / Exit</h2>

      {readiness && (
        <div className={styles.readiness}>
          <div className={ui.flexBetween}>
            <span>Sale readiness</span>
            <span className={readiness.is_ready ? ui.badge : ui.badgeDanger}>
              {readiness.is_ready ? "ready" : "not ready"}
            </span>
          </div>
          <span className={ui.faintText}>Open tickets: {readiness.open_tickets}</span>
          <span className={ui.faintText}>Active lease: {readiness.has_active_lease ? "yes" : "no"}</span>
          <span className={ui.faintText}>Unsettled insurance claims: {readiness.unsettled_insurance_claims}</span>
          <span className={ui.faintText}>
            Incomplete renovation projects: {readiness.incomplete_renovation_projects}
          </span>
        </div>
      )}

      <ul className={styles.list}>
        {sales.map((sale) => (
          <li key={sale.id} className={styles.item}>
            <div className={styles.itemRow}>
              <div className={styles.itemInfo}>
                <span>
                  {sale.buyer_name ?? "No buyer yet"}
                  {sale.listing_price != null ? ` — listed ${sale.listing_price}` : ""}
                </span>
                <span className={ui.faintText}>
                  {sale.status.replace(/_/g, " ")}
                  {sale.sale_price != null ? ` — sold ${sale.sale_price}` : ""}
                </span>
              </div>
              {sale.status !== "completed" && sale.status !== "cancelled" && (
                <button
                  type="button"
                  onClick={() => handleComplete(sale.id)}
                  disabled={busy}
                  className={`${ui.btnPrimary} ${ui.btnSmall}`}
                >
                  Complete sale
                </button>
              )}
            </div>
            <div className={styles.checklist}>
              <label className={ui.field}>
                <input
                  type="checkbox"
                  checked={sale.ownership_transferred}
                  onChange={() => handleToggleTransfer(sale, "ownership_transferred")}
                />
                Ownership transferred
              </label>
              <label className={ui.field}>
                <input
                  type="checkbox"
                  checked={sale.utilities_transferred}
                  onChange={() => handleToggleTransfer(sale, "utilities_transferred")}
                />
                Utilities transferred
              </label>
              <label className={ui.field}>
                <input
                  type="checkbox"
                  checked={sale.society_transferred}
                  onChange={() => handleToggleTransfer(sale, "society_transferred")}
                />
                Society transferred
              </label>
            </div>
          </li>
        ))}
        {sales.length === 0 && <p className={ui.mutedText}>No sale record yet.</p>}
      </ul>

      <div className={styles.formRow}>
        <label className={ui.field}>
          Listing price
          <input
            type="number"
            className={ui.input}
            value={draft.listing_price}
            onChange={(e) => setDraft((prev) => ({ ...prev, listing_price: e.target.value }))}
          />
        </label>
        <label className={ui.field}>
          Buyer name
          <input
            className={ui.input}
            value={draft.buyer_name}
            onChange={(e) => setDraft((prev) => ({ ...prev, buyer_name: e.target.value }))}
          />
        </label>
        <label className={ui.field}>
          Buyer contact
          <input
            className={ui.input}
            value={draft.buyer_contact}
            onChange={(e) => setDraft((prev) => ({ ...prev, buyer_contact: e.target.value }))}
          />
        </label>
        <button type="button" onClick={handleCreate} disabled={busy} className={ui.btnPrimary}>
          Start sale
        </button>
      </div>
      {error && <p className={ui.errorText}>{error}</p>}
    </section>
  );
}
