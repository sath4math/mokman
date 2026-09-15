"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent, type ReactNode } from "react";

import type { AuthorizedRepresentative, OwnerProfile, OwnershipType } from "@/lib/types";

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
};

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="flex flex-col gap-1 text-sm">
      {label}
      {children}
    </label>
  );
}

const inputClass =
  "rounded border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900";

export function ProfileForm({
  initialProfile,
  initialRepresentatives,
}: {
  initialProfile: OwnerProfile | null;
  initialRepresentatives: AuthorizedRepresentative[];
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
      const response = await fetch("/api/backend/owner/profile", {
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
    <div className="flex flex-col gap-10">
      <form onSubmit={handleSubmit} className="flex flex-col gap-8">
        <section className="flex flex-col gap-4">
          <h2 className="text-lg font-medium">KYC</h2>
          <Field label="PAN number">
            <input
              className={inputClass}
              value={profile.pan_number ?? ""}
              onChange={(e) => set("pan_number", e.target.value)}
            />
          </Field>
          <div className="grid grid-cols-2 gap-4">
            <Field label="ID proof type">
              <select
                className={inputClass}
                value={profile.id_proof_type ?? "aadhaar"}
                onChange={(e) => set("id_proof_type", e.target.value)}
              >
                <option value="aadhaar">Aadhaar</option>
                <option value="passport">Passport</option>
              </select>
            </Field>
            <Field label="ID proof number">
              <input
                className={inputClass}
                value={profile.id_proof_number ?? ""}
                onChange={(e) => set("id_proof_number", e.target.value)}
              />
            </Field>
          </div>
        </section>

        <section className="flex flex-col gap-4">
          <h2 className="text-lg font-medium">Bank details</h2>
          <Field label="Bank name">
            <input
              className={inputClass}
              value={profile.bank_name ?? ""}
              onChange={(e) => set("bank_name", e.target.value)}
            />
          </Field>
          <div className="grid grid-cols-2 gap-4">
            <Field label="Account number">
              <input
                className={inputClass}
                value={profile.bank_account_number ?? ""}
                onChange={(e) => set("bank_account_number", e.target.value)}
              />
            </Field>
            <Field label="IFSC">
              <input
                className={inputClass}
                value={profile.bank_ifsc ?? ""}
                onChange={(e) => set("bank_ifsc", e.target.value)}
              />
            </Field>
          </div>
        </section>

        <section className="flex flex-col gap-4">
          <h2 className="text-lg font-medium">Ownership</h2>
          <div className="grid grid-cols-2 gap-4">
            <Field label="Ownership type">
              <select
                className={inputClass}
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
                  type="number"
                  min={0}
                  max={100}
                  className={inputClass}
                  value={profile.ownership_percentage ?? ""}
                  onChange={(e) =>
                    set("ownership_percentage", e.target.value ? Number(e.target.value) : null)
                  }
                />
              </Field>
            )}
          </div>
        </section>

        <section className="flex flex-col gap-4">
          <h2 className="text-lg font-medium">Nominee</h2>
          <div className="grid grid-cols-3 gap-4">
            <Field label="Name">
              <input
                className={inputClass}
                value={profile.nominee_name ?? ""}
                onChange={(e) => set("nominee_name", e.target.value)}
              />
            </Field>
            <Field label="Relationship">
              <input
                className={inputClass}
                value={profile.nominee_relationship ?? ""}
                onChange={(e) => set("nominee_relationship", e.target.value)}
              />
            </Field>
            <Field label="Phone">
              <input
                className={inputClass}
                value={profile.nominee_phone ?? ""}
                onChange={(e) => set("nominee_phone", e.target.value)}
              />
            </Field>
          </div>
        </section>

        <section className="flex flex-col gap-4">
          <h2 className="text-lg font-medium">Emergency contact</h2>
          <div className="grid grid-cols-2 gap-4">
            <Field label="Name">
              <input
                className={inputClass}
                value={profile.emergency_contact_name ?? ""}
                onChange={(e) => set("emergency_contact_name", e.target.value)}
              />
            </Field>
            <Field label="Phone">
              <input
                className={inputClass}
                value={profile.emergency_contact_phone ?? ""}
                onChange={(e) => set("emergency_contact_phone", e.target.value)}
              />
            </Field>
          </div>
        </section>

        {error && <p className="text-sm text-red-600">{error}</p>}
        {saved && <p className="text-sm text-emerald-600">Saved.</p>}
        <button
          type="submit"
          disabled={saving}
          className="w-fit rounded bg-zinc-900 px-5 py-2 text-white disabled:opacity-50 dark:bg-zinc-50 dark:text-zinc-900"
        >
          {saving ? "Saving…" : "Save profile"}
        </button>
      </form>

      <section className="flex flex-col gap-4 border-t border-zinc-200 pt-8 dark:border-zinc-800">
        <h2 className="text-lg font-medium">Authorized representatives</h2>
        <ul className="flex flex-col gap-2">
          {representatives.map((rep) => (
            <li
              key={rep.id}
              className="flex items-center justify-between rounded border border-zinc-200 px-4 py-2 text-sm dark:border-zinc-800"
            >
              <span>
                {rep.name}
                {rep.relationship ? ` (${rep.relationship})` : ""} — {rep.phone ?? rep.email ?? "no contact"}
              </span>
              <button
                type="button"
                onClick={() => handleRemoveRepresentative(rep.id)}
                className="text-red-600 underline"
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <input
            className={inputClass}
            placeholder="Name"
            value={repDraft.name}
            onChange={(e) => setRepDraft((prev) => ({ ...prev, name: e.target.value }))}
          />
          <input
            className={inputClass}
            placeholder="Relationship"
            value={repDraft.relationship}
            onChange={(e) => setRepDraft((prev) => ({ ...prev, relationship: e.target.value }))}
          />
          <input
            className={inputClass}
            placeholder="Phone"
            value={repDraft.phone}
            onChange={(e) => setRepDraft((prev) => ({ ...prev, phone: e.target.value }))}
          />
          <button
            type="button"
            onClick={handleAddRepresentative}
            className="rounded border border-zinc-300 px-3 py-2 text-sm dark:border-zinc-700"
          >
            Add
          </button>
        </div>
      </section>
    </div>
  );
}
