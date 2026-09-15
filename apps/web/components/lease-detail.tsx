"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { DocumentVault } from "@/components/document-vault";
import type { DocumentRecord, Inspection, Lease, RentInvoice } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./lease-detail.module.css";

const INSPECTION_LABELS: Record<"move_in" | "move_out", string> = {
  move_in: "Move-in inspection",
  move_out: "Move-out inspection",
};

const PAYMENT_METHODS = ["upi", "bank_transfer", "cash", "cheque", "other"];

export function LeaseDetail({
  lease: initialLease,
  viewerRole,
  documents,
  inspections: initialInspections,
  invoices: initialInvoices,
}: {
  lease: Lease;
  viewerRole: "owner" | "tenant";
  documents: DocumentRecord[];
  inspections: Inspection[];
  invoices: RentInvoice[];
}) {
  const router = useRouter();
  const [lease, setLease] = useState(initialLease);
  const [inspections, setInspections] = useState(initialInspections);
  const [invoices, setInvoices] = useState(initialInvoices);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [paymentDraft, setPaymentDraft] = useState({ amount: "", method: PAYMENT_METHODS[0], reference_note: "" });

  const hasAcknowledged =
    viewerRole === "owner" ? !!lease.owner_acknowledged_at : !!lease.tenant_acknowledged_at;

  async function handleAcknowledge() {
    setError(null);
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/leases/${lease.id}/acknowledge`, { method: "POST" });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to acknowledge lease");
        return;
      }
      setLease(data);
      router.refresh();
    } finally {
      setBusy(false);
    }
  }

  async function handleTerminate() {
    setError(null);
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/leases/${lease.id}/terminate`, { method: "POST" });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to terminate lease");
        return;
      }
      setLease(data);
      router.refresh();
    } finally {
      setBusy(false);
    }
  }

  async function handleCreateInspection(type: "move_in" | "move_out") {
    setError(null);
    setBusy(true);
    try {
      const response = await fetch("/api/backend/inspections", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          property_id: lease.property_id,
          lease_id: lease.id,
          inspection_type: type,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to create inspection");
        return;
      }
      setInspections((prev) => [...prev, data as Inspection]);
    } finally {
      setBusy(false);
    }
  }

  async function handleSignOff(id: string) {
    setError(null);
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/inspections/${id}/sign-off`, { method: "POST" });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to sign off");
        return;
      }
      setInspections((prev) => prev.map((i) => (i.id === data.id ? data : i)));
    } finally {
      setBusy(false);
    }
  }

  async function handleDepositUpdate(
    id: string,
    field: "deposit_deduction" | "deposit_refund",
    value: string,
  ) {
    const response = await fetch(`/api/backend/inspections/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ [field]: value ? Number(value) : null }),
    });
    if (response.ok) {
      const updated = (await response.json()) as Inspection;
      setInspections((prev) => prev.map((i) => (i.id === updated.id ? updated : i)));
    }
  }

  async function handleRecordPayment(invoiceId: string) {
    if (!paymentDraft.amount) return;
    setError(null);
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/rent/invoices/${invoiceId}/payments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          amount: Number(paymentDraft.amount),
          method: paymentDraft.method,
          reference_note: paymentDraft.reference_note || null,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to record payment");
        return;
      }
      setInvoices((prev) => prev.map((inv) => (inv.id === data.id ? data : inv)));
      setPaymentDraft({ amount: "", method: PAYMENT_METHODS[0], reference_note: "" });
      router.refresh();
    } finally {
      setBusy(false);
    }
  }

  async function handleSettleDeposit(id: string) {
    setError(null);
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/inspections/${id}/settle-deposit`, { method: "POST" });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to settle deposit");
        return;
      }
      setInspections((prev) => prev.map((i) => (i.id === data.id ? data : i)));
    } finally {
      setBusy(false);
    }
  }

  const moveIn = inspections.find((i) => i.inspection_type === "move_in");
  const moveOut = inspections.find((i) => i.inspection_type === "move_out");
  const payableInvoice = invoices.find((inv) => inv.status === "pending" || inv.status === "partially_paid" || inv.status === "overdue");

  return (
    <div className={styles.wrapper}>
      <section className={ui.card}>
        <div className={ui.flexBetween}>
          <h2 className={styles.sectionTitle}>Lease terms</h2>
          <span className={ui.badge}>{lease.status.replace(/_/g, " ")}</span>
        </div>
        <div className={styles.termsGrid}>
          <div>
            <div className={ui.faintText}>Start</div>
            <div>{lease.start_date}</div>
          </div>
          <div>
            <div className={ui.faintText}>End</div>
            <div>{lease.end_date}</div>
          </div>
          <div>
            <div className={ui.faintText}>Monthly rent</div>
            <div>{lease.monthly_rent}</div>
          </div>
          <div>
            <div className={ui.faintText}>Security deposit</div>
            <div>{lease.security_deposit}</div>
          </div>
          <div>
            <div className={ui.faintText}>Lock-in (months)</div>
            <div>{lease.lock_in_period_months ?? "—"}</div>
          </div>
          <div>
            <div className={ui.faintText}>Notice period (days)</div>
            <div>{lease.notice_period_days ?? "—"}</div>
          </div>
          <div>
            <div className={ui.faintText}>Annual escalation</div>
            <div>{lease.annual_escalation_percentage ? `${lease.annual_escalation_percentage}%` : "—"}</div>
          </div>
          <div>
            <div className={ui.faintText}>Owner acknowledged</div>
            <div>{lease.owner_acknowledged_at ? "Yes" : "No"}</div>
          </div>
          <div>
            <div className={ui.faintText}>Tenant acknowledged</div>
            <div>{lease.tenant_acknowledged_at ? "Yes" : "No"}</div>
          </div>
        </div>
        {lease.responsibilities && (
          <div>
            <div className={ui.faintText}>Responsibilities</div>
            <p>{lease.responsibilities}</p>
          </div>
        )}
        <div className={ui.flexRow}>
          {lease.status === "pending_acknowledgment" && !hasAcknowledged && (
            <button type="button" onClick={handleAcknowledge} disabled={busy} className={ui.btnPrimary}>
              Acknowledge lease
            </button>
          )}
          {lease.status === "active" && (
            <button type="button" onClick={handleTerminate} disabled={busy} className={ui.btnSecondary}>
              Terminate lease
            </button>
          )}
        </div>
        {error && <p className={ui.errorText}>{error}</p>}
      </section>

      <section className={ui.card}>
        <h2 className={styles.sectionTitle}>Rent</h2>
        <div className={styles.invoiceList}>
          {invoices.map((invoice) => (
            <div key={invoice.id} className={styles.invoiceRow}>
              <span>
                {invoice.period_start} – {invoice.period_end}
              </span>
              <span className={ui.faintText}>Due {invoice.due_date}</span>
              <span>{invoice.amount_due}</span>
              <span className={ui.badge}>{invoice.status.replace(/_/g, " ")}</span>
            </div>
          ))}
          {invoices.length === 0 && <p className={ui.mutedText}>No invoices yet.</p>}
        </div>
        {payableInvoice && (
          <div className={styles.paymentForm}>
            <p className={ui.faintText}>
              Record a payment against the {payableInvoice.period_start} invoice (
              {payableInvoice.amount_due} due)
            </p>
            <div className={styles.paymentRow}>
              <label className={ui.field}>
                Amount
                <input
                  type="number"
                  className={ui.input}
                  value={paymentDraft.amount}
                  onChange={(e) => setPaymentDraft((prev) => ({ ...prev, amount: e.target.value }))}
                />
              </label>
              <label className={ui.field}>
                Method
                <select
                  className={ui.select}
                  value={paymentDraft.method}
                  onChange={(e) => setPaymentDraft((prev) => ({ ...prev, method: e.target.value }))}
                >
                  {PAYMENT_METHODS.map((method) => (
                    <option key={method} value={method}>
                      {method.replace(/_/g, " ")}
                    </option>
                  ))}
                </select>
              </label>
              <label className={ui.field}>
                Reference note
                <input
                  className={ui.input}
                  placeholder="UPI txn id, cheque no., etc."
                  value={paymentDraft.reference_note}
                  onChange={(e) => setPaymentDraft((prev) => ({ ...prev, reference_note: e.target.value }))}
                />
              </label>
              <button
                type="button"
                onClick={() => handleRecordPayment(payableInvoice.id)}
                disabled={busy}
                className={ui.btnPrimary}
              >
                Record payment
              </button>
            </div>
          </div>
        )}
      </section>

      <section className={ui.card}>
        <h2 className={styles.sectionTitle}>Inspections</h2>
        <div className={styles.inspectionsList}>
          {(["move_in", "move_out"] as const).map((type) => {
            const inspection = type === "move_in" ? moveIn : moveOut;
            if (!inspection) {
              return (
                <div key={type} className={styles.inspectionRow}>
                  <span>{INSPECTION_LABELS[type]}</span>
                  <button
                    type="button"
                    onClick={() => handleCreateInspection(type)}
                    disabled={busy}
                    className={ui.linkPrimary}
                  >
                    Start {INSPECTION_LABELS[type].toLowerCase()}
                  </button>
                </div>
              );
            }
            const fullySigned = !!inspection.owner_signed_off_at && !!inspection.tenant_signed_off_at;
            const viewerSigned =
              viewerRole === "owner" ? !!inspection.owner_signed_off_at : !!inspection.tenant_signed_off_at;
            return (
              <div key={inspection.id} className={styles.inspectionCard}>
                <div className={ui.flexBetween}>
                  <span>{INSPECTION_LABELS[type]}</span>
                  <span className={ui.badge}>{fullySigned ? "signed off" : "pending sign-off"}</span>
                </div>
                {type === "move_out" && (
                  <div className={styles.depositRow}>
                    <label className={ui.field}>
                      Deposit deduction
                      <input
                        type="number"
                        className={ui.input}
                        defaultValue={inspection.deposit_deduction ?? ""}
                        disabled={fullySigned}
                        onBlur={(e) => handleDepositUpdate(inspection.id, "deposit_deduction", e.target.value)}
                      />
                    </label>
                    <label className={ui.field}>
                      Deposit refund
                      <input
                        type="number"
                        className={ui.input}
                        defaultValue={inspection.deposit_refund ?? ""}
                        disabled={fullySigned}
                        onBlur={(e) => handleDepositUpdate(inspection.id, "deposit_refund", e.target.value)}
                      />
                    </label>
                  </div>
                )}
                {!viewerSigned && (
                  <button
                    type="button"
                    onClick={() => handleSignOff(inspection.id)}
                    disabled={busy}
                    className={`${ui.btnPrimary} ${ui.btnSmall}`}
                  >
                    Sign off
                  </button>
                )}
                {type === "move_out" && fullySigned && !inspection.settled_at && (
                  <button
                    type="button"
                    onClick={() => handleSettleDeposit(inspection.id)}
                    disabled={busy}
                    className={`${ui.btnSecondary} ${ui.btnSmall}`}
                  >
                    Settle deposit
                  </button>
                )}
                {inspection.settled_at && <p className={ui.successText}>Deposit settled.</p>}
              </div>
            );
          })}
        </div>
      </section>

      <DocumentVault
        ownerType="lease"
        ownerId={lease.id}
        initialDocuments={documents}
        documentTypes={["lease_agreement", "id_proof", "other"]}
      />
    </div>
  );
}
