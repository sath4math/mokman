"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState, type FormEvent } from "react";

import ui from "@/styles/ui.module.css";

import styles from "./new-lease.module.css";

function NewLeaseFields() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const propertyId = searchParams.get("property_id") ?? "";

  const [form, setForm] = useState({
    tenant_email: "",
    start_date: "",
    end_date: "",
    monthly_rent: "",
    security_deposit: "",
    lock_in_period_months: "",
    notice_period_days: "",
    annual_escalation_percentage: "",
    responsibilities: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function set(key: keyof typeof form, value: string) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const body = {
        property_id: propertyId,
        tenant_email: form.tenant_email,
        start_date: form.start_date,
        end_date: form.end_date,
        monthly_rent: Number(form.monthly_rent),
        security_deposit: Number(form.security_deposit),
        lock_in_period_months: form.lock_in_period_months ? Number(form.lock_in_period_months) : null,
        notice_period_days: form.notice_period_days ? Number(form.notice_period_days) : null,
        annual_escalation_percentage: form.annual_escalation_percentage
          ? Number(form.annual_escalation_percentage)
          : null,
        responsibilities: form.responsibilities || null,
      };
      const response = await fetch("/api/backend/leases", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to create lease");
        return;
      }
      router.push(`/owner/leases/${data.id}`);
      router.refresh();
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className={styles.main}>
      <h1 className={styles.title}>Create Lease</h1>
      <form onSubmit={handleSubmit} className={styles.form}>
        <label className={ui.field}>
          Tenant email
          <input
            required
            type="email"
            className={ui.input}
            placeholder="tenant@example.com"
            value={form.tenant_email}
            onChange={(e) => set("tenant_email", e.target.value)}
          />
        </label>
        <div className={styles.row2}>
          <label className={ui.field}>
            Start date
            <input
              required
              type="date"
              className={ui.input}
              value={form.start_date}
              onChange={(e) => set("start_date", e.target.value)}
            />
          </label>
          <label className={ui.field}>
            End date
            <input
              required
              type="date"
              className={ui.input}
              value={form.end_date}
              onChange={(e) => set("end_date", e.target.value)}
            />
          </label>
        </div>
        <div className={styles.row2}>
          <label className={ui.field}>
            Monthly rent
            <input
              required
              type="number"
              className={ui.input}
              value={form.monthly_rent}
              onChange={(e) => set("monthly_rent", e.target.value)}
            />
          </label>
          <label className={ui.field}>
            Security deposit
            <input
              required
              type="number"
              className={ui.input}
              value={form.security_deposit}
              onChange={(e) => set("security_deposit", e.target.value)}
            />
          </label>
        </div>
        <div className={styles.row2}>
          <label className={ui.field}>
            Lock-in period (months)
            <input
              type="number"
              className={ui.input}
              value={form.lock_in_period_months}
              onChange={(e) => set("lock_in_period_months", e.target.value)}
            />
          </label>
          <label className={ui.field}>
            Notice period (days)
            <input
              type="number"
              className={ui.input}
              value={form.notice_period_days}
              onChange={(e) => set("notice_period_days", e.target.value)}
            />
          </label>
        </div>
        <label className={ui.field}>
          Annual escalation (%)
          <input
            type="number"
            className={ui.input}
            value={form.annual_escalation_percentage}
            onChange={(e) => set("annual_escalation_percentage", e.target.value)}
          />
        </label>
        <label className={ui.field}>
          Responsibilities
          <textarea
            className={ui.textarea}
            rows={3}
            value={form.responsibilities}
            onChange={(e) => set("responsibilities", e.target.value)}
          />
        </label>
        {error && <p className={ui.errorText}>{error}</p>}
        <button type="submit" disabled={submitting || !propertyId} className={`${ui.btnPrimary} ${styles.submitButton}`}>
          {submitting ? "Creating…" : "Create lease"}
        </button>
      </form>
    </main>
  );
}

export function NewLeaseForm() {
  return (
    <Suspense>
      <NewLeaseFields />
    </Suspense>
  );
}
