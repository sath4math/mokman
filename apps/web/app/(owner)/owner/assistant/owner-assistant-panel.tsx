"use client";

import { useState } from "react";

import ui from "@/styles/ui.module.css";

import styles from "./assistant.module.css";

export function OwnerAssistantPanel() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAsk() {
    if (!question.trim()) return;
    setBusy(true);
    setError(null);
    setAnswer(null);
    try {
      const response = await fetch("/api/backend/assistant/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to get an answer");
        return;
      }
      setAnswer(data.answer);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className={styles.section}>
      <p className={ui.mutedText}>
        Ask about your portfolio — rent status, open maintenance, upcoming lease expiries, pending
        approvals, and dues.
      </p>
      <div className={styles.askRow}>
        <label className={ui.field}>
          Question
          <textarea
            className={ui.textarea}
            rows={2}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g. Is any of my rent overdue?"
          />
        </label>
        <button type="button" onClick={handleAsk} disabled={busy || !question.trim()} className={ui.btnPrimary}>
          {busy ? "Asking…" : "Ask"}
        </button>
      </div>
      {answer && (
        <div className={styles.answerBlock}>
          <div className={ui.faintText}>Answer</div>
          <p>{answer}</p>
        </div>
      )}
      {error && <p className={ui.errorText}>{error}</p>}
    </section>
  );
}
