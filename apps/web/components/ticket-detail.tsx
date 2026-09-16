"use client";

import { useState } from "react";

import { DocumentVault } from "@/components/document-vault";
import { enqueueAction } from "@/lib/offline-queue";
import type { DocumentRecord, FieldStaffUser, MaintenanceTicket, Vendor } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./ticket-detail.module.css";

type Candidate = { value: string; label: string };

export function TicketDetail({
  ticket: initialTicket,
  viewerRole,
  viewerId,
  documents,
  staff,
  vendors,
}: {
  ticket: MaintenanceTicket;
  viewerRole: "owner" | "tenant" | "field_staff" | "admin";
  viewerId: string;
  documents: DocumentRecord[];
  staff: FieldStaffUser[];
  vendors: Vendor[];
}) {
  const [ticket, setTicket] = useState(initialTicket);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const staffCandidates: Candidate[] = staff.map((s) => ({
    value: `staff:${s.id}`,
    label: s.full_name ?? s.email ?? s.id,
  }));
  const vendorCandidates: Candidate[] = vendors.map((v) => ({
    value: `vendor:${v.id}`,
    label: `${v.name} (${v.service_category})`,
  }));
  const [assignee, setAssignee] = useState(staffCandidates[0]?.value ?? vendorCandidates[0]?.value ?? "");
  const [resolutionNotes, setResolutionNotes] = useState("");
  const [ratingScore, setRatingScore] = useState(5);
  const [ratingNotes, setRatingNotes] = useState("");
  const [ratingSubmitted, setRatingSubmitted] = useState(false);
  const [inspectionDate, setInspectionDate] = useState("");
  const [inspectionScheduled, setInspectionScheduled] = useState(false);
  const [queued, setQueued] = useState(false);

  const isManager = viewerRole === "owner" || viewerRole === "admin";
  const isAssignee = viewerRole === "field_staff" && ticket.assigned_to === viewerId;
  const isRaiser = ticket.raised_by === viewerId;

  async function post(path: string, body?: object) {
    setError(null);
    setBusy(true);
    const url = `/api/backend/maintenance/tickets/${ticket.id}${path}`;
    try {
      // Field staff work from job sites with unreliable connectivity — queue
      // the action locally instead of failing outright. Other roles act from
      // an office context and don't need this (no service worker is even
      // registered outside /field, so this only ever triggers there).
      if (viewerRole === "field_staff" && !navigator.onLine) {
        await enqueueAction({ url, method: "POST", body });
        setQueued(true);
        return;
      }
      const response = await fetch(url, {
        method: "POST",
        headers: body ? { "Content-Type": "application/json" } : undefined,
        body: body ? JSON.stringify(body) : undefined,
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Action failed");
        return;
      }
      setTicket(data);
    } catch {
      if (viewerRole === "field_staff") {
        await enqueueAction({ url, method: "POST", body });
        setQueued(true);
      } else {
        setError("Network error — action not saved");
      }
    } finally {
      setBusy(false);
    }
  }

  async function handleAssign() {
    if (!assignee) return;
    const [type, id] = assignee.split(":");
    await post("/assign", type === "vendor" ? { assigned_vendor_id: id } : { assigned_to: id });
  }

  async function handleResolve() {
    if (!resolutionNotes.trim()) return;
    await post("/resolve", { resolution_notes: resolutionNotes });
    setResolutionNotes("");
  }

  async function handleRate() {
    if (!ticket.assigned_vendor_id) return;
    setError(null);
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/vendors/${ticket.assigned_vendor_id}/ratings`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticket_id: ticket.id, score: ratingScore, notes: ratingNotes || null }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to submit rating");
        return;
      }
      setRatingSubmitted(true);
    } finally {
      setBusy(false);
    }
  }

  async function handleScheduleInspection() {
    if (!inspectionDate) return;
    setError(null);
    setBusy(true);
    try {
      const response = await fetch("/api/backend/inspections", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          property_id: ticket.property_id,
          inspection_type: "ticket_triggered",
          triggered_by_ticket_id: ticket.id,
          scheduled_for: inspectionDate,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to schedule inspection");
        return;
      }
      setInspectionScheduled(true);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className={styles.wrapper}>
      <section className={ui.card}>
        <div className={ui.flexBetween}>
          <h2 className={styles.sectionTitle}>{ticket.category}</h2>
          <span className={ui.flexRow}>
            {ticket.sla_breached_at && <span className={ui.badgeDanger}>SLA breached</span>}
            <span className={ui.badge}>{ticket.status.replace(/_/g, " ")}</span>
          </span>
        </div>
        <div className={styles.meta}>
          <span className={ui.faintText}>Priority: {ticket.priority}</span>
          <p>{ticket.description}</p>
        </div>

        {ticket.resolution_notes && (
          <div className={styles.resolutionBlock}>
            <div className={ui.faintText}>Resolution notes</div>
            <p>{ticket.resolution_notes}</p>
          </div>
        )}

        {isManager &&
          (ticket.status === "open" || ticket.status === "assigned") &&
          (staffCandidates.length > 0 || vendorCandidates.length > 0) && (
            <div className={styles.assignRow}>
              <label className={ui.field}>
                Assign to
                <select className={ui.select} value={assignee} onChange={(e) => setAssignee(e.target.value)}>
                  {staffCandidates.length > 0 && (
                    <optgroup label="Field Staff">
                      {staffCandidates.map((c) => (
                        <option key={c.value} value={c.value}>
                          {c.label}
                        </option>
                      ))}
                    </optgroup>
                  )}
                  {vendorCandidates.length > 0 && (
                    <optgroup label="Vendors">
                      {vendorCandidates.map((c) => (
                        <option key={c.value} value={c.value}>
                          {c.label}
                        </option>
                      ))}
                    </optgroup>
                  )}
                </select>
              </label>
              <button type="button" onClick={handleAssign} disabled={busy} className={ui.btnPrimary}>
                {ticket.assigned_to || ticket.assigned_vendor_id ? "Reassign" : "Assign"}
              </button>
            </div>
          )}

        <div className={ui.flexRow}>
          {(isAssignee || isManager) && ticket.status === "assigned" && (
            <button type="button" onClick={() => post("/start")} disabled={busy} className={ui.btnPrimary}>
              Start work
            </button>
          )}

          {(isAssignee || isManager) && ticket.status === "in_progress" && (
            <div className={styles.resolveForm}>
              <label className={ui.field}>
                Resolution notes
                <textarea
                  className={ui.textarea}
                  rows={2}
                  value={resolutionNotes}
                  onChange={(e) => setResolutionNotes(e.target.value)}
                />
              </label>
              <button
                type="button"
                onClick={handleResolve}
                disabled={busy}
                className={`${ui.btnPrimary} ${ui.btnSmall}`}
              >
                Mark resolved
              </button>
            </div>
          )}

          {isManager && ticket.status === "resolved" && (
            <button type="button" onClick={() => post("/close")} disabled={busy} className={ui.btnPrimary}>
              Close ticket
            </button>
          )}

          {(isManager || isRaiser) && ticket.status === "closed" && (
            <button type="button" onClick={() => post("/reopen")} disabled={busy} className={ui.btnSecondary}>
              Reopen
            </button>
          )}
        </div>

        {isManager && (
          <div className={styles.resolveForm}>
            {inspectionScheduled ? (
              <p className={ui.mutedText}>Inspection scheduled.</p>
            ) : (
              <>
                <label className={ui.field}>
                  Schedule inspection for
                  <input
                    type="date"
                    className={ui.input}
                    value={inspectionDate}
                    onChange={(e) => setInspectionDate(e.target.value)}
                  />
                </label>
                <button
                  type="button"
                  onClick={handleScheduleInspection}
                  disabled={busy || !inspectionDate}
                  className={`${ui.btnSecondary} ${ui.btnSmall}`}
                >
                  Schedule inspection
                </button>
              </>
            )}
          </div>
        )}

        {isManager && ticket.status === "closed" && ticket.assigned_vendor_id && (
          <div className={styles.resolveForm}>
            {ratingSubmitted ? (
              <p className={ui.mutedText}>Vendor rated — thanks.</p>
            ) : (
              <>
                <label className={ui.field}>
                  Rate vendor (1-5)
                  <select
                    className={ui.select}
                    value={ratingScore}
                    onChange={(e) => setRatingScore(Number(e.target.value))}
                  >
                    {[1, 2, 3, 4, 5].map((n) => (
                      <option key={n} value={n}>
                        {n}
                      </option>
                    ))}
                  </select>
                </label>
                <label className={ui.field}>
                  Notes
                  <input
                    className={ui.input}
                    value={ratingNotes}
                    onChange={(e) => setRatingNotes(e.target.value)}
                  />
                </label>
                <button
                  type="button"
                  onClick={handleRate}
                  disabled={busy}
                  className={`${ui.btnSecondary} ${ui.btnSmall}`}
                >
                  Submit rating
                </button>
              </>
            )}
          </div>
        )}
        {queued && (
          <p className={ui.mutedText}>Offline — action queued, will sync when back online.</p>
        )}
        {error && <p className={ui.errorText}>{error}</p>}
      </section>

      <DocumentVault
        ownerType="ticket"
        ownerId={ticket.id}
        initialDocuments={documents}
        documentTypes={["photo", "other"]}
      />
    </div>
  );
}
