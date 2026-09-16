"use client";

import { useState } from "react";

import type { InvestmentSummary } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./investment-panel.module.css";

function formatPercent(value: number | null): string {
  return value == null ? "—" : `${value.toFixed(1)}%`;
}

export function InvestmentPanel({
  propertyId,
  initialSummary,
}: {
  propertyId: string;
  initialSummary: InvestmentSummary | null;
}) {
  const [summary, setSummary] = useState(initialSummary);
  const [draft, setDraft] = useState({
    purchase_price: initialSummary?.purchase_price?.toString() ?? "",
    current_market_value: initialSummary?.current_market_value?.toString() ?? "",
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recommendation, setRecommendation] = useState<string | null>(null);
  const [recommending, setRecommending] = useState(false);

  async function handleSave() {
    setError(null);
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/properties/${propertyId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          purchase_price: draft.purchase_price ? Number(draft.purchase_price) : null,
          current_market_value: draft.current_market_value ? Number(draft.current_market_value) : null,
        }),
      });
      if (!response.ok) {
        const data = await response.json();
        setError(data.detail ?? "Failed to update investment details");
        return;
      }
      const summaryResponse = await fetch(`/api/backend/properties/${propertyId}/investment-summary`);
      if (summaryResponse.ok) {
        setSummary(await summaryResponse.json());
      }
    } finally {
      setBusy(false);
    }
  }

  async function handleRecommend() {
    setRecommending(true);
    setError(null);
    try {
      const response = await fetch(`/api/backend/assistant/properties/${propertyId}/investment-recommendation`, {
        method: "POST",
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to get a recommendation");
        return;
      }
      setRecommendation(data.answer);
    } finally {
      setRecommending(false);
    }
  }

  return (
    <section className={styles.section}>
      <h2 className={styles.heading}>Investment</h2>

      {summary && (
        <div className={styles.metricsGrid}>
          <div className={styles.metric}>
            <span className={ui.faintText}>Appreciation</span>
            <strong>{formatPercent(summary.appreciation_percentage)}</strong>
          </div>
          <div className={styles.metric}>
            <span className={ui.faintText}>Gross yield</span>
            <strong>{formatPercent(summary.gross_yield_percentage)}</strong>
          </div>
          <div className={styles.metric}>
            <span className={ui.faintText}>ROI</span>
            <strong>{formatPercent(summary.roi_percentage)}</strong>
          </div>
          <div className={styles.metric}>
            <span className={ui.faintText}>Trailing 12mo rent income</span>
            <strong>{summary.trailing_12_month_rent_income}</strong>
          </div>
          <div className={styles.metric}>
            <span className={ui.faintText}>All-time net income</span>
            <strong>{summary.total_net_income_all_time}</strong>
          </div>
        </div>
      )}

      <div className={styles.formRow}>
        <label className={ui.field}>
          Purchase price
          <input
            type="number"
            className={ui.input}
            value={draft.purchase_price}
            onChange={(e) => setDraft((prev) => ({ ...prev, purchase_price: e.target.value }))}
          />
        </label>
        <label className={ui.field}>
          Current market value
          <input
            type="number"
            className={ui.input}
            value={draft.current_market_value}
            onChange={(e) => setDraft((prev) => ({ ...prev, current_market_value: e.target.value }))}
          />
        </label>
        <button type="button" onClick={handleSave} disabled={busy} className={ui.btnPrimary}>
          Save
        </button>
        <button
          type="button"
          onClick={handleRecommend}
          disabled={recommending}
          className={`${ui.btnSecondary} ${ui.btnSmall}`}
        >
          {recommending ? "Thinking…" : "Get sell/hold opinion"}
        </button>
      </div>
      {recommendation && (
        <div>
          <p className={ui.faintText}>Advisory only — not financial advice</p>
          <p className={ui.mutedText}>{recommendation}</p>
        </div>
      )}
      {error && <p className={ui.errorText}>{error}</p>}
    </section>
  );
}
