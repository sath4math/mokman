"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent, type ReactNode } from "react";

import type { TenantProfile } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./profile.module.css";

const EMPTY_PROFILE: TenantProfile = {
  id_proof_type: "aadhaar",
  id_proof_number: "",
  occupants_count: null,
  vehicles: [],
  pets: [],
  emergency_contact_name: "",
  emergency_contact_phone: "",
  verification_status: "pending",
};

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className={ui.field}>
      {label}
      {children}
    </label>
  );
}

export function ProfileForm({ initialProfile }: { initialProfile: TenantProfile | null }) {
  const router = useRouter();
  const [profile, setProfile] = useState<TenantProfile>(initialProfile ?? EMPTY_PROFILE);
  const [vehiclesText, setVehiclesText] = useState((initialProfile?.vehicles ?? []).join(", "));
  const [petsText, setPetsText] = useState((initialProfile?.pets ?? []).join(", "));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  function set<K extends keyof TenantProfile>(key: K, value: TenantProfile[K]) {
    setProfile((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSaved(false);
    setSaving(true);
    try {
      const body = {
        ...profile,
        vehicles: vehiclesText
          ? vehiclesText.split(",").map((v) => v.trim()).filter(Boolean)
          : [],
        pets: petsText
          ? petsText.split(",").map((p) => p.trim()).filter(Boolean)
          : [],
      };
      const response = await fetch("/api/backend/tenant/profile", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!response.ok) {
        const data = await response.json();
        setError(data.detail ?? "Failed to save profile");
        return;
      }
      setSaved(true);
      router.refresh();
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>ID proof</h2>
        <div className={styles.row2}>
          <Field label="ID proof type">
            <select
              className={ui.select}
              value={profile.id_proof_type ?? "aadhaar"}
              onChange={(e) => set("id_proof_type", e.target.value)}
            >
              <option value="aadhaar">Aadhaar</option>
              <option value="passport">Passport</option>
            </select>
          </Field>
          <Field label="ID proof number">
            <input
              className={ui.input}
              value={profile.id_proof_number ?? ""}
              onChange={(e) => set("id_proof_number", e.target.value)}
            />
          </Field>
        </div>
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Household</h2>
        <div className={styles.row2}>
          <Field label="Occupants count">
            <input
              type="number"
              min={0}
              className={ui.input}
              value={profile.occupants_count ?? ""}
              onChange={(e) => set("occupants_count", e.target.value ? Number(e.target.value) : null)}
            />
          </Field>
        </div>
        <div className={styles.row2}>
          <Field label="Vehicles (comma-separated)">
            <input
              className={ui.input}
              placeholder="KA01AB1234"
              value={vehiclesText}
              onChange={(e) => setVehiclesText(e.target.value)}
            />
          </Field>
          <Field label="Pets (comma-separated)">
            <input
              className={ui.input}
              placeholder="dog, cat"
              value={petsText}
              onChange={(e) => setPetsText(e.target.value)}
            />
          </Field>
        </div>
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Emergency contact</h2>
        <div className={styles.row2}>
          <Field label="Name">
            <input
              className={ui.input}
              value={profile.emergency_contact_name ?? ""}
              onChange={(e) => set("emergency_contact_name", e.target.value)}
            />
          </Field>
          <Field label="Phone">
            <input
              className={ui.input}
              value={profile.emergency_contact_phone ?? ""}
              onChange={(e) => set("emergency_contact_phone", e.target.value)}
            />
          </Field>
        </div>
      </section>

      {error && <p className={ui.errorText}>{error}</p>}
      {saved && <p className={ui.successText}>Saved.</p>}
      <button type="submit" disabled={saving} className={`${ui.btnPrimary} ${styles.submitButton}`}>
        {saving ? "Saving…" : "Save profile"}
      </button>
    </form>
  );
}
