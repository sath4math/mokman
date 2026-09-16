"use client";

import { useRef, useState } from "react";

import type { DocumentRecord } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import styles from "./document-vault.module.css";

const DEFAULT_DOCUMENT_TYPES = ["photo", "floor_plan", "ownership_deed", "tax_receipt", "other"];

export function DocumentVault({
  ownerType,
  ownerId,
  initialDocuments,
  documentTypes = DEFAULT_DOCUMENT_TYPES,
}: {
  ownerType: string;
  ownerId: string;
  initialDocuments: DocumentRecord[];
  documentTypes?: string[];
}) {
  const [documents, setDocuments] = useState(initialDocuments);
  const [documentType, setDocumentType] = useState(documentTypes[0]);
  const [expiryDate, setExpiryDate] = useState("");
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [askingId, setAskingId] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [askBusy, setAskBusy] = useState(false);
  const [askError, setAskError] = useState<string | null>(null);

  async function handleUpload() {
    const file = fileInputRef.current?.files?.[0];
    if (!file) return;
    setError(null);
    setUploading(true);
    try {
      const presignResponse = await fetch("/api/backend/documents/presign", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          owner_type: ownerType,
          owner_id: ownerId,
          filename: file.name,
          content_type: file.type || "application/octet-stream",
        }),
      });
      if (!presignResponse.ok) {
        setError("Failed to prepare upload");
        return;
      }
      const { upload_url, s3_key } = await presignResponse.json();

      const uploadResponse = await fetch(upload_url, {
        method: "PUT",
        headers: { "Content-Type": file.type || "application/octet-stream" },
        body: file,
      });
      if (!uploadResponse.ok) {
        setError("Upload to storage failed");
        return;
      }

      const confirmResponse = await fetch("/api/backend/documents", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          owner_type: ownerType,
          owner_id: ownerId,
          document_type: documentType,
          s3_key,
          expiry_date: expiryDate || null,
        }),
      });
      if (!confirmResponse.ok) {
        setError("Failed to save document record");
        return;
      }
      const document = (await confirmResponse.json()) as DocumentRecord;
      setDocuments((prev) => [...prev, document]);
      if (fileInputRef.current) fileInputRef.current.value = "";
      setExpiryDate("");
    } finally {
      setUploading(false);
    }
  }

  async function handleDownload(id: string) {
    const response = await fetch(`/api/backend/documents/${id}/download`);
    if (!response.ok) return;
    const { download_url } = await response.json();
    window.open(download_url, "_blank");
  }

  async function handleDelete(id: string) {
    const response = await fetch(`/api/backend/documents/${id}`, { method: "DELETE" });
    if (response.ok) {
      setDocuments((prev) => prev.filter((d) => d.id !== id));
    }
  }

  function toggleAsk(id: string) {
    setAskingId((prev) => (prev === id ? null : id));
    setQuestion("");
    setAnswer(null);
    setAskError(null);
  }

  async function handleAsk() {
    if (!askingId || !question.trim()) return;
    setAskBusy(true);
    setAskError(null);
    setAnswer(null);
    try {
      const response = await fetch(`/api/backend/assistant/documents/${askingId}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await response.json();
      if (!response.ok) {
        setAskError(data.detail ?? "Failed to get an answer");
        return;
      }
      setAnswer(data.answer);
    } finally {
      setAskBusy(false);
    }
  }

  return (
    <section className={styles.section}>
      <h2 className={styles.heading}>Documents</h2>

      <ul className={styles.list}>
        {documents.map((doc) => (
          <li key={doc.id} className={styles.item}>
            <span>
              {doc.document_type}
              {doc.expiry_date ? ` — expires ${doc.expiry_date}` : ""}
            </span>
            <span className={styles.itemActions}>
              <button type="button" onClick={() => handleDownload(doc.id)} className={ui.link}>
                Download
              </button>
              <button type="button" onClick={() => toggleAsk(doc.id)} className={ui.link}>
                {askingId === doc.id ? "Cancel" : "Ask a question"}
              </button>
              <button type="button" onClick={() => handleDelete(doc.id)} className={ui.linkDanger}>
                Delete
              </button>
            </span>
            {askingId === doc.id && (
              <div className={styles.uploadRow}>
                <label className={ui.field}>
                  Question
                  <input
                    className={ui.input}
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                  />
                </label>
                <button type="button" onClick={handleAsk} disabled={askBusy} className={ui.btnSecondary}>
                  {askBusy ? "Asking…" : "Ask"}
                </button>
                {answer && <p className={ui.mutedText}>{answer}</p>}
                {askError && <p className={ui.errorText}>{askError}</p>}
              </div>
            )}
          </li>
        ))}
        {documents.length === 0 && <p className={ui.mutedText}>No documents uploaded yet.</p>}
      </ul>

      <div className={styles.uploadRow}>
        <label className={ui.field}>
          Type
          <select
            className={ui.select}
            value={documentType}
            onChange={(e) => setDocumentType(e.target.value)}
          >
            {documentTypes.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </label>
        <label className={ui.field}>
          Expiry date (optional)
          <input
            type="date"
            className={ui.input}
            value={expiryDate}
            onChange={(e) => setExpiryDate(e.target.value)}
          />
        </label>
        <label className={ui.field}>
          File
          <input ref={fileInputRef} type="file" />
        </label>
        <button type="button" onClick={handleUpload} disabled={uploading} className={ui.btnPrimary}>
          {uploading ? "Uploading…" : "Upload"}
        </button>
      </div>
      {error && <p className={ui.errorText}>{error}</p>}
    </section>
  );
}
