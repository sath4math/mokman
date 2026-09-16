"use client";

import { useState } from "react";

import type { InsuranceClaim, InsurancePolicy } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./insurance-panel.module.css";

export function InsurancePanel({
  propertyId,
  initialPolicies,
}: {
  propertyId: string;
  initialPolicies: InsurancePolicy[];
}) {
  const [policies, setPolicies] = useState(initialPolicies);
  const [draft, setDraft] = useState({
    policy_number: "",
    insurer_name: "",
    category: "",
    premium_amount: "",
    start_date: "",
    end_date: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [claimsById, setClaimsById] = useState<Record<string, InsuranceClaim[]>>({});
  const [claimDraft, setClaimDraft] = useState({ incident_date: "", description: "", claim_amount: "" });

  async function handleCreate() {
    if (!draft.policy_number.trim() || !draft.insurer_name.trim() || !draft.start_date || !draft.end_date) return;
    setError(null);
    setBusy(true);
    try {
      const response = await fetch("/api/backend/insurance/policies", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          property_id: propertyId,
          policy_number: draft.policy_number,
          insurer_name: draft.insurer_name,
          category: draft.category || "property",
          premium_amount: Number(draft.premium_amount || 0),
          start_date: draft.start_date,
          end_date: draft.end_date,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to add policy");
        return;
      }
      setPolicies((prev) => [...prev, data]);
      setDraft({ policy_number: "", insurer_name: "", category: "", premium_amount: "", start_date: "", end_date: "" });
    } finally {
      setBusy(false);
    }
  }

  async function toggleExpand(id: string) {
    const next = expandedId === id ? null : id;
    setExpandedId(next);
    if (next && !(next in claimsById)) {
      const response = await fetch(`/api/backend/insurance/policies/${next}/claims`);
      const data = response.ok ? await response.json() : [];
      setClaimsById((prev) => ({ ...prev, [next]: Array.isArray(data) ? data : [] }));
    }
  }

  async function handleFileClaim(policyId: string) {
    if (!claimDraft.incident_date || !claimDraft.description.trim() || !claimDraft.claim_amount) return;
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/insurance/policies/${policyId}/claims`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          incident_date: claimDraft.incident_date,
          description: claimDraft.description,
          claim_amount: Number(claimDraft.claim_amount),
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to file claim");
        return;
      }
      setClaimsById((prev) => ({ ...prev, [policyId]: [...(prev[policyId] ?? []), data] }));
      setClaimDraft({ incident_date: "", description: "", claim_amount: "" });
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className={styles.section}>
      <h2 className={styles.heading}>Insurance</h2>
      <ul className={styles.list}>
        {policies.map((policy) => (
          <li key={policy.id} className={styles.item}>
            <div className={styles.itemRow}>
              <div className={styles.itemInfo}>
                <span>
                  {policy.insurer_name} — {policy.policy_number} ({policy.category})
                </span>
                <span className={ui.faintText}>
                  Premium {policy.premium_amount}, {policy.start_date} to {policy.end_date}
                </span>
              </div>
              <button type="button" onClick={() => toggleExpand(policy.id)} className={ui.link}>
                {expandedId === policy.id ? "Hide claims" : "Claims"}
              </button>
            </div>
            {expandedId === policy.id && (
              <div className={styles.claims}>
                {(claimsById[policy.id] ?? []).map((claim) => (
                  <div key={claim.id} className={ui.flexBetween}>
                    <span>
                      {claim.incident_date}: {claim.description} — {claim.claim_amount}
                    </span>
                    <span className={ui.badge}>{claim.status.replace(/_/g, " ")}</span>
                  </div>
                ))}
                {(claimsById[policy.id] ?? []).length === 0 && (
                  <p className={ui.mutedText}>No claims filed yet.</p>
                )}
                <div className={styles.formRow}>
                  <label className={ui.field}>
                    Incident date
                    <input
                      type="date"
                      className={ui.input}
                      value={claimDraft.incident_date}
                      onChange={(e) => setClaimDraft((prev) => ({ ...prev, incident_date: e.target.value }))}
                    />
                  </label>
                  <label className={ui.field}>
                    Description
                    <input
                      className={ui.input}
                      value={claimDraft.description}
                      onChange={(e) => setClaimDraft((prev) => ({ ...prev, description: e.target.value }))}
                    />
                  </label>
                  <label className={ui.field}>
                    Claim amount
                    <input
                      type="number"
                      className={ui.input}
                      value={claimDraft.claim_amount}
                      onChange={(e) => setClaimDraft((prev) => ({ ...prev, claim_amount: e.target.value }))}
                    />
                  </label>
                  <button
                    type="button"
                    onClick={() => handleFileClaim(policy.id)}
                    disabled={busy}
                    className={`${ui.btnSecondary} ${ui.btnSmall}`}
                  >
                    File claim
                  </button>
                </div>
              </div>
            )}
          </li>
        ))}
        {policies.length === 0 && <p className={ui.mutedText}>No insurance policies recorded yet.</p>}
      </ul>

      <div className={styles.formRow}>
        <label className={ui.field}>
          Policy number
          <input
            className={ui.input}
            value={draft.policy_number}
            onChange={(e) => setDraft((prev) => ({ ...prev, policy_number: e.target.value }))}
          />
        </label>
        <label className={ui.field}>
          Insurer
          <input
            className={ui.input}
            value={draft.insurer_name}
            onChange={(e) => setDraft((prev) => ({ ...prev, insurer_name: e.target.value }))}
          />
        </label>
        <label className={ui.field}>
          Category
          <input
            className={ui.input}
            placeholder="property, contents..."
            value={draft.category}
            onChange={(e) => setDraft((prev) => ({ ...prev, category: e.target.value }))}
          />
        </label>
        <label className={ui.field}>
          Premium
          <input
            type="number"
            className={ui.input}
            value={draft.premium_amount}
            onChange={(e) => setDraft((prev) => ({ ...prev, premium_amount: e.target.value }))}
          />
        </label>
        <label className={ui.field}>
          Start date
          <input
            type="date"
            className={ui.input}
            value={draft.start_date}
            onChange={(e) => setDraft((prev) => ({ ...prev, start_date: e.target.value }))}
          />
        </label>
        <label className={ui.field}>
          End date
          <input
            type="date"
            className={ui.input}
            value={draft.end_date}
            onChange={(e) => setDraft((prev) => ({ ...prev, end_date: e.target.value }))}
          />
        </label>
        <button type="button" onClick={handleCreate} disabled={busy} className={ui.btnPrimary}>
          Add policy
        </button>
      </div>
      {error && <p className={ui.errorText}>{error}</p>}
    </section>
  );
}
