"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent, type ReactNode } from "react";

import { DocumentVault } from "@/components/document-vault";
import type { AuthorizedRepresentative, DocumentRecord, OwnerProfile, OwnershipType } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import { PackageOfferings } from "./package-offerings";
import styles from "./profile.module.css";

const KYC_DOCUMENT_TYPES = ["pan_card", "id_proof"];

const EMPTY_PROFILE: OwnerProfile = {
  pan_number: "",
  id_proof_type: "aadhaar",
  id_proof_number: "",
  bank_account_number: "",
  bank_ifsc: "",
  bank_name: "",
  ownership_type: "single",
  ownership_percentage: null,
  nominee_name: "",
  nominee_relationship: "",
  nominee_phone: "",
  emergency_contact_name: "",
  emergency_contact_phone: "",
  kyc_status: "pending",
  package: "starter",
};

const PACKAGE_LABELS: Record<OwnerProfile["package"], string> = {
  starter: "Starter — self-serve digital record-keeping",
  managed: "Managed — rent handled for you",
  full_care: "Full Care — full operations handled for you",
  complete: "Complete — everything, including in-house workforce & intelligence",
};

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className={ui.field}>
      {label}
      {children}
    </label>
  );
}

export function ProfileForm({
  ownerId,
  mode = "self",
  initialProfile,
  initialRepresentatives,
  initialDocuments,
}: {
  ownerId: string;
  /** "admin" submits on the owner's behalf via the admin-only endpoint;
   * "self" (default) is the owner's own self-service save. */
  mode?: "self" | "admin";
  initialProfile: OwnerProfile | null;
  initialRepresentatives: AuthorizedRepresentative[];
  initialDocuments: DocumentRecord[];
}) {
  const router = useRouter();
  const [profile, setProfile] = useState<OwnerProfile>(initialProfile ?? EMPTY_PROFILE);
  const [representatives, setRepresentatives] = useState(initialRepresentatives);
  const [repDraft, setRepDraft] = useState({ name: "", relationship: "", phone: "", email: "" });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  function set<K extends keyof OwnerProfile>(key: K, value: OwnerProfile[K]) {
    setProfile((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSaved(false);
    setSaving(true);
    try {
      const url = mode === "admin" ? `/api/backend/owner/profiles/${ownerId}` : "/api/backend/owner/profile";
      const response = await fetch(url, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(profile),
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

  async function handleAddRepresentative() {
    if (!repDraft.name) return;
    const response = await fetch("/api/backend/owner/profile/representatives", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(repDraft),
    });
    if (response.ok) {
      const rep = (await response.json()) as AuthorizedRepresentative;
      setRepresentatives((prev) => [...prev, rep]);
      setRepDraft({ name: "", relationship: "", phone: "", email: "" });
    }
  }

  async function handleRemoveRepresentative(id: string) {
    const response = await fetch(`/api/backend/owner/profile/representatives/${id}`, {
      method: "DELETE",
    });
    if (response.ok) {
      setRepresentatives((prev) => prev.filter((rep) => rep.id !== id));
    }
  }

  return (
    <div className={styles.formWrapper}>
      <form onSubmit={handleSubmit} className={styles.form}>
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Plan</h2>
          <Field label="Package">
            <select
              className={ui.select}
              value={profile.package}
              onChange={(e) => set("package", e.target.value as OwnerProfile["package"])}
            >
              {Object.entries(PACKAGE_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </Field>
          <PackageOfferings package={profile.package} />
        </section>

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>KYC</h2>
          <p className={ui.mutedText}>
            Every field below is required, along with at least one uploaded document (PAN card or ID
            proof), before this profile can be saved and sent for admin review.
          </p>

          <DocumentVault
            ownerType="owner_profile"
            ownerId={ownerId}
            initialDocuments={initialDocuments}
            documentTypes={KYC_DOCUMENT_TYPES}
          />

          <Field label="PAN number">
            <input
              required
              className={ui.input}
              value={profile.pan_number ?? ""}
              onChange={(e) => set("pan_number", e.target.value)}
            />
          </Field>
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
                required
                className={ui.input}
                value={profile.id_proof_number ?? ""}
                onChange={(e) => set("id_proof_number", e.target.value)}
              />
            </Field>
          </div>
        </section>

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Bank details</h2>
          <Field label="Bank name">
            <input
              required
              className={ui.input}
              value={profile.bank_name ?? ""}
              onChange={(e) => set("bank_name", e.target.value)}
            />
          </Field>
          <div className={styles.row2}>
            <Field label="Account number">
              <input
                required
                className={ui.input}
                value={profile.bank_account_number ?? ""}
                onChange={(e) => set("bank_account_number", e.target.value)}
              />
            </Field>
            <Field label="IFSC">
              <input
                required
                className={ui.input}
                value={profile.bank_ifsc ?? ""}
                onChange={(e) => set("bank_ifsc", e.target.value)}
              />
            </Field>
          </div>
        </section>

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Ownership</h2>
          <div className={styles.row2}>
            <Field label="Ownership type">
              <select
                className={ui.select}
                value={profile.ownership_type}
                onChange={(e) => set("ownership_type", e.target.value as OwnershipType)}
              >
                <option value="single">Single</option>
                <option value="joint">Joint</option>
              </select>
            </Field>
            {profile.ownership_type === "joint" && (
              <Field label="Your ownership %">
                <input
                  required
                  type="number"
                  min={0}
                  max={100}
                  className={ui.input}
                  value={profile.ownership_percentage ?? ""}
                  onChange={(e) =>
                    set("ownership_percentage", e.target.value ? Number(e.target.value) : null)
                  }
                />
              </Field>
            )}
          </div>
        </section>

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Nominee</h2>
          <div className={styles.row3}>
            <Field label="Name">
              <input
                required
                className={ui.input}
                value={profile.nominee_name ?? ""}
                onChange={(e) => set("nominee_name", e.target.value)}
              />
            </Field>
            <Field label="Relationship">
              <input
                required
                className={ui.input}
                value={profile.nominee_relationship ?? ""}
                onChange={(e) => set("nominee_relationship", e.target.value)}
              />
            </Field>
            <Field label="Phone">
              <input
                required
                className={ui.input}
                value={profile.nominee_phone ?? ""}
                onChange={(e) => set("nominee_phone", e.target.value)}
              />
            </Field>
          </div>
        </section>

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Emergency contact</h2>
          <div className={styles.row2}>
            <Field label="Name">
              <input
                required
                className={ui.input}
                value={profile.emergency_contact_name ?? ""}
                onChange={(e) => set("emergency_contact_name", e.target.value)}
              />
            </Field>
            <Field label="Phone">
              <input
                required
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

      {mode === "self" && (
        <section className={styles.repSection}>
          <h2 className={styles.sectionTitle}>Authorized representatives</h2>
          <ul className={styles.repList}>
            {representatives.map((rep) => (
              <li key={rep.id} className={styles.repItem}>
                <span>
                  {rep.name}
                  {rep.relationship ? ` (${rep.relationship})` : ""} — {rep.phone ?? rep.email ?? "no contact"}
                </span>
                <button
                  type="button"
                  onClick={() => handleRemoveRepresentative(rep.id)}
                  className={ui.linkDanger}
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
          <div className={styles.repForm}>
            <input
              className={ui.input}
              placeholder="Name"
              value={repDraft.name}
              onChange={(e) => setRepDraft((prev) => ({ ...prev, name: e.target.value }))}
            />
            <input
              className={ui.input}
              placeholder="Relationship"
              value={repDraft.relationship}
              onChange={(e) => setRepDraft((prev) => ({ ...prev, relationship: e.target.value }))}
            />
            <input
              className={ui.input}
              placeholder="Phone"
              value={repDraft.phone}
              onChange={(e) => setRepDraft((prev) => ({ ...prev, phone: e.target.value }))}
            />
            <button type="button" onClick={handleAddRepresentative} className={ui.btnSecondary}>
              Add
            </button>
          </div>
        </section>
      )}
    </div>
  );
}
