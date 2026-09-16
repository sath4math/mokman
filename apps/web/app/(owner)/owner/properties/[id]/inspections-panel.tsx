"use client";

import { useState } from "react";

import { DocumentVault } from "@/components/document-vault";
import type { DocumentRecord, Inspection } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./inspections-panel.module.css";

const TYPE_LABELS: Record<Inspection["inspection_type"], string> = {
  move_in: "Move-in",
  move_out: "Move-out",
  scheduled: "Scheduled",
  ticket_triggered: "Ticket-triggered",
};

export function InspectionsPanel({
  propertyId,
  initialInspections,
}: {
  propertyId: string;
  initialInspections: Inspection[];
}) {
  const [inspections, setInspections] = useState(initialInspections);
  const [scheduledFor, setScheduledFor] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [photosById, setPhotosById] = useState<Record<string, DocumentRecord[]>>({});
  const [analysisById, setAnalysisById] = useState<Record<string, string>>({});
  const [analyzeBusyId, setAnalyzeBusyId] = useState<string | null>(null);
  const [analyzeErrorById, setAnalyzeErrorById] = useState<Record<string, string>>({});

  async function toggleExpand(id: string) {
    const next = expandedId === id ? null : id;
    setExpandedId(next);
    if (next && !(next in photosById)) {
      const response = await fetch(`/api/backend/documents?owner_type=inspection&owner_id=${next}`);
      const data = response.ok ? await response.json() : [];
      setPhotosById((prev) => ({ ...prev, [next]: Array.isArray(data) ? data : [] }));
    }
  }

  async function handleAnalyze(id: string) {
    setAnalyzeBusyId(id);
    setAnalyzeErrorById((prev) => ({ ...prev, [id]: "" }));
    try {
      const response = await fetch(`/api/backend/assistant/inspections/${id}/analyze`, { method: "POST" });
      const data = await response.json();
      if (!response.ok) {
        setAnalyzeErrorById((prev) => ({ ...prev, [id]: data.detail ?? "Failed to analyze photos" }));
        return;
      }
      setAnalysisById((prev) => ({ ...prev, [id]: data.answer }));
    } finally {
      setAnalyzeBusyId(null);
    }
  }

  async function handleSchedule() {
    if (!scheduledFor) return;
    setError(null);
    setBusy(true);
    try {
      const response = await fetch("/api/backend/inspections", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          property_id: propertyId,
          inspection_type: "scheduled",
          scheduled_for: scheduledFor,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to schedule inspection");
        return;
      }
      setInspections((prev) => [...prev, data]);
      setScheduledFor("");
    } finally {
      setBusy(false);
    }
  }

  const sorted = [...inspections].sort((a, b) => {
    const aDate = a.scheduled_for ?? "";
    const bDate = b.scheduled_for ?? "";
    return bDate.localeCompare(aDate);
  });

  return (
    <section className={styles.section}>
      <h2 className={styles.heading}>Inspections</h2>
      <ul className={styles.list}>
        {sorted.map((inspection) => (
          <li key={inspection.id} className={styles.item}>
            <div className={styles.itemRow}>
              <div className={styles.itemInfo}>
                <span>
                  {TYPE_LABELS[inspection.inspection_type]}
                  {inspection.scheduled_for ? ` — ${inspection.scheduled_for}` : ""}
                </span>
                {inspection.follow_up_notes && (
                  <span className={ui.faintText}>
                    Follow-up: {inspection.follow_up_notes}
                    {inspection.follow_up_due_on ? ` (by ${inspection.follow_up_due_on})` : ""}
                  </span>
                )}
              </div>
              <span className={ui.flexRow}>
                {inspection.settled_at && <span className={ui.badge}>settled</span>}
                <button type="button" onClick={() => toggleExpand(inspection.id)} className={ui.link}>
                  {expandedId === inspection.id ? "Hide photos" : "Photos"}
                </button>
              </span>
            </div>
            {expandedId === inspection.id && (
              <div className={styles.expanded}>
                <DocumentVault
                  key={`${inspection.id}-${inspection.id in photosById}`}
                  ownerType="inspection"
                  ownerId={inspection.id}
                  initialDocuments={photosById[inspection.id] ?? []}
                  documentTypes={["before_photo", "after_photo", "photo", "other"]}
                />
                <button
                  type="button"
                  onClick={() => handleAnalyze(inspection.id)}
                  disabled={analyzeBusyId === inspection.id}
                  className={ui.btnSecondary}
                >
                  {analyzeBusyId === inspection.id ? "Analyzing…" : "Analyze photos"}
                </button>
                {analysisById[inspection.id] && (
                  <p className={ui.mutedText}>{analysisById[inspection.id]}</p>
                )}
                {analyzeErrorById[inspection.id] && (
                  <p className={ui.errorText}>{analyzeErrorById[inspection.id]}</p>
                )}
              </div>
            )}
          </li>
        ))}
        {inspections.length === 0 && <p className={ui.mutedText}>No inspections yet.</p>}
      </ul>

      <div className={styles.formRow}>
        <label className={ui.field}>
          Schedule an inspection for
          <input
            type="date"
            className={ui.input}
            value={scheduledFor}
            onChange={(e) => setScheduledFor(e.target.value)}
          />
        </label>
        <button type="button" onClick={handleSchedule} disabled={busy || !scheduledFor} className={ui.btnPrimary}>
          Schedule
        </button>
      </div>
      {error && <p className={ui.errorText}>{error}</p>}
    </section>
  );
}
