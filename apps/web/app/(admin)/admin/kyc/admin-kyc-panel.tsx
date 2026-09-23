"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import type { KycStatus, OwnerProfileAdmin } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./kyc.module.css";

const TABS: { value: KycStatus | "all"; label: string }[] = [
  { value: "pending", label: "Pending" },
  { value: "verified", label: "Verified" },
  { value: "rejected", label: "Rejected" },
  { value: "all", label: "All" },
];

export function AdminKycPanel({ initialProfiles }: { initialProfiles: OwnerProfileAdmin[] }) {
  const [profiles, setProfiles] = useState(initialProfiles);
  const [tab, setTab] = useState<KycStatus | "all">("pending");
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

  const visible = useMemo(
    () => (tab === "all" ? profiles : profiles.filter((p) => p.kyc_status === tab)),
    [profiles, tab],
  );

  async function handleApprove(profile: OwnerProfileAdmin) {
    setError(null);
    setBusyId(profile.user_id);
    try {
      const response = await fetch(`/api/backend/owner/profiles/${profile.user_id}/kyc/approve`, {
        method: "POST",
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to approve KYC");
        return;
      }
      setProfiles((prev) => prev.map((p) => (p.user_id === profile.user_id ? { ...p, ...data } : p)));
    } finally {
      setBusyId(null);
    }
  }

  async function handleReject(profile: OwnerProfileAdmin) {
    const reason = window.prompt(`Reason for rejecting ${profile.full_name ?? profile.email}'s KYC?`);
    if (!reason) return;
    setError(null);
    setBusyId(profile.user_id);
    try {
      const response = await fetch(`/api/backend/owner/profiles/${profile.user_id}/kyc/reject`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to reject KYC");
        return;
      }
      setProfiles((prev) => prev.map((p) => (p.user_id === profile.user_id ? { ...p, ...data } : p)));
    } finally {
      setBusyId(null);
    }
  }

  return (
    <section className={styles.section}>
      <div className={styles.tabs}>
        {TABS.map((t) => (
          <button
            key={t.value}
            type="button"
            onClick={() => setTab(t.value)}
            className={t.value === tab ? ui.btnPrimary : ui.btnSecondary}
          >
            {t.label}
          </button>
        ))}
      </div>

      {error && <p className={ui.errorText}>{error}</p>}

      <ul className={styles.list}>
        {visible.map((profile) => (
          <li key={profile.user_id} className={styles.item}>
            <div className={styles.itemInfo}>
              <span>{profile.full_name ?? "(no name)"} — {profile.email ?? "(no email)"}</span>
              <span className={ui.faintText}>
                PAN: {profile.pan_number ?? "—"} · {profile.id_proof_type ?? "no ID type"}:{" "}
                {profile.id_proof_number ?? "—"}
              </span>
            </div>
            <span className={ui.flexRow}>
              <span className={profile.kyc_status === "rejected" ? ui.badgeDanger : ui.badge}>
                {profile.kyc_status}
              </span>
              <button
                type="button"
                onClick={() => handleApprove(profile)}
                disabled={busyId === profile.user_id || profile.kyc_status === "verified"}
                className={ui.btnSecondary}
              >
                Approve
              </button>
              <button
                type="button"
                onClick={() => handleReject(profile)}
                disabled={busyId === profile.user_id || profile.kyc_status === "rejected"}
                className={ui.linkDanger}
              >
                Reject
              </button>
              <Link href={`/admin/owners/${profile.user_id}`} className={ui.link}>
                Manage on behalf of
              </Link>
            </span>
          </li>
        ))}
        {visible.length === 0 && <p className={ui.mutedText}>No owner profiles in this view.</p>}
      </ul>
    </section>
  );
}
