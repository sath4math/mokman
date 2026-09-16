"use client";

import { useState } from "react";

import type { ProjectMilestone, RenovationProject } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./renovation-panel.module.css";

export function RenovationPanel({
  propertyId,
  initialProjects,
}: {
  propertyId: string;
  initialProjects: RenovationProject[];
}) {
  const [projects, setProjects] = useState(initialProjects);
  const [draft, setDraft] = useState({ title: "", description: "", budget_amount: "" });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [milestonesById, setMilestonesById] = useState<Record<string, ProjectMilestone[]>>({});
  const [milestoneDraft, setMilestoneDraft] = useState({ title: "", due_date: "", payment_amount: "" });

  async function handleCreate() {
    if (!draft.title.trim()) return;
    setError(null);
    setBusy(true);
    try {
      const response = await fetch("/api/backend/renovation/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          property_id: propertyId,
          title: draft.title,
          description: draft.description || null,
          budget_amount: draft.budget_amount ? Number(draft.budget_amount) : null,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to add project");
        return;
      }
      setProjects((prev) => [...prev, data]);
      setDraft({ title: "", description: "", budget_amount: "" });
    } finally {
      setBusy(false);
    }
  }

  async function toggleExpand(id: string) {
    const next = expandedId === id ? null : id;
    setExpandedId(next);
    if (next && !(next in milestonesById)) {
      const response = await fetch(`/api/backend/renovation/projects/${next}/milestones`);
      const data = response.ok ? await response.json() : [];
      setMilestonesById((prev) => ({ ...prev, [next]: Array.isArray(data) ? data : [] }));
    }
  }

  async function handleAddMilestone(projectId: string) {
    if (!milestoneDraft.title.trim() || !milestoneDraft.payment_amount) return;
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/renovation/projects/${projectId}/milestones`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: milestoneDraft.title,
          due_date: milestoneDraft.due_date || null,
          payment_amount: Number(milestoneDraft.payment_amount),
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to add milestone");
        return;
      }
      setMilestonesById((prev) => ({ ...prev, [projectId]: [...(prev[projectId] ?? []), data] }));
      setMilestoneDraft({ title: "", due_date: "", payment_amount: "" });
    } finally {
      setBusy(false);
    }
  }

  async function handleCompleteMilestone(projectId: string, milestoneId: string) {
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/renovation/milestones/${milestoneId}/complete`, {
        method: "POST",
      });
      const data = await response.json();
      if (response.ok) {
        setMilestonesById((prev) => ({
          ...prev,
          [projectId]: (prev[projectId] ?? []).map((m) => (m.id === milestoneId ? data : m)),
        }));
      }
    } finally {
      setBusy(false);
    }
  }

  async function handlePayMilestone(projectId: string, milestoneId: string) {
    setBusy(true);
    try {
      const response = await fetch(`/api/backend/renovation/milestones/${milestoneId}/pay`, { method: "POST" });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to pay milestone");
        return;
      }
      setMilestonesById((prev) => ({
        ...prev,
        [projectId]: (prev[projectId] ?? []).map((m) => (m.id === milestoneId ? data : m)),
      }));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className={styles.section}>
      <h2 className={styles.heading}>Renovation projects</h2>
      <ul className={styles.list}>
        {projects.map((project) => (
          <li key={project.id} className={styles.item}>
            <div className={styles.itemRow}>
              <div className={styles.itemInfo}>
                <span>{project.title}</span>
                <span className={ui.faintText}>
                  {project.budget_amount != null ? `Budget ${project.budget_amount} — ` : ""}
                  {project.status.replace(/_/g, " ")}
                </span>
              </div>
              <button type="button" onClick={() => toggleExpand(project.id)} className={ui.link}>
                {expandedId === project.id ? "Hide milestones" : "Milestones"}
              </button>
            </div>
            {expandedId === project.id && (
              <div className={styles.milestones}>
                {(milestonesById[project.id] ?? []).map((milestone) => (
                  <div key={milestone.id} className={ui.flexBetween}>
                    <span>
                      {milestone.title} — {milestone.payment_amount}
                      {milestone.due_date ? ` (due ${milestone.due_date})` : ""}
                    </span>
                    <span className={ui.flexRow}>
                      {!milestone.completed_at && (
                        <button
                          type="button"
                          onClick={() => handleCompleteMilestone(project.id, milestone.id)}
                          disabled={busy}
                          className={`${ui.btnSecondary} ${ui.btnSmall}`}
                        >
                          Complete
                        </button>
                      )}
                      {milestone.paid_at ? (
                        <span className={ui.badge}>paid</span>
                      ) : (
                        <button
                          type="button"
                          onClick={() => handlePayMilestone(project.id, milestone.id)}
                          disabled={busy}
                          className={`${ui.btnPrimary} ${ui.btnSmall}`}
                        >
                          Pay
                        </button>
                      )}
                    </span>
                  </div>
                ))}
                {(milestonesById[project.id] ?? []).length === 0 && (
                  <p className={ui.mutedText}>No milestones yet.</p>
                )}
                <div className={styles.formRow}>
                  <label className={ui.field}>
                    Title
                    <input
                      className={ui.input}
                      value={milestoneDraft.title}
                      onChange={(e) => setMilestoneDraft((prev) => ({ ...prev, title: e.target.value }))}
                    />
                  </label>
                  <label className={ui.field}>
                    Due date
                    <input
                      type="date"
                      className={ui.input}
                      value={milestoneDraft.due_date}
                      onChange={(e) => setMilestoneDraft((prev) => ({ ...prev, due_date: e.target.value }))}
                    />
                  </label>
                  <label className={ui.field}>
                    Payment amount
                    <input
                      type="number"
                      className={ui.input}
                      value={milestoneDraft.payment_amount}
                      onChange={(e) => setMilestoneDraft((prev) => ({ ...prev, payment_amount: e.target.value }))}
                    />
                  </label>
                  <button
                    type="button"
                    onClick={() => handleAddMilestone(project.id)}
                    disabled={busy}
                    className={`${ui.btnSecondary} ${ui.btnSmall}`}
                  >
                    Add milestone
                  </button>
                </div>
              </div>
            )}
          </li>
        ))}
        {projects.length === 0 && <p className={ui.mutedText}>No renovation projects yet.</p>}
      </ul>

      <div className={styles.formRow}>
        <label className={ui.field}>
          Title
          <input
            className={ui.input}
            value={draft.title}
            onChange={(e) => setDraft((prev) => ({ ...prev, title: e.target.value }))}
          />
        </label>
        <label className={ui.field}>
          Description
          <input
            className={ui.input}
            value={draft.description}
            onChange={(e) => setDraft((prev) => ({ ...prev, description: e.target.value }))}
          />
        </label>
        <label className={ui.field}>
          Budget
          <input
            type="number"
            className={ui.input}
            value={draft.budget_amount}
            onChange={(e) => setDraft((prev) => ({ ...prev, budget_amount: e.target.value }))}
          />
        </label>
        <button type="button" onClick={handleCreate} disabled={busy} className={ui.btnPrimary}>
          Add project
        </button>
      </div>
      {error && <p className={ui.errorText}>{error}</p>}
    </section>
  );
}
