"use client";

import { useRef, useState } from "react";

import type { DocumentRecord } from "@/lib/types";

const DOCUMENT_TYPES = ["photo", "floor_plan", "ownership_deed", "tax_receipt", "other"];

export function DocumentVault({
  propertyId,
  initialDocuments,
}: {
  propertyId: string;
  initialDocuments: DocumentRecord[];
}) {
  const [documents, setDocuments] = useState(initialDocuments);
  const [documentType, setDocumentType] = useState(DOCUMENT_TYPES[0]);
  const [expiryDate, setExpiryDate] = useState("");
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
          owner_type: "property",
          owner_id: propertyId,
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
          owner_type: "property",
          owner_id: propertyId,
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

  return (
    <section className="flex flex-col gap-4">
      <h2 className="text-lg font-medium">Documents</h2>

      <ul className="flex flex-col gap-2">
        {documents.map((doc) => (
          <li
            key={doc.id}
            className="flex items-center justify-between rounded border border-zinc-200 px-4 py-2 text-sm dark:border-zinc-800"
          >
            <span>
              {doc.document_type}
              {doc.expiry_date ? ` — expires ${doc.expiry_date}` : ""}
            </span>
            <span className="flex gap-3">
              <button type="button" onClick={() => handleDownload(doc.id)} className="underline">
                Download
              </button>
              <button
                type="button"
                onClick={() => handleDelete(doc.id)}
                className="text-red-600 underline"
              >
                Delete
              </button>
            </span>
          </li>
        ))}
        {documents.length === 0 && (
          <p className="text-sm text-zinc-600 dark:text-zinc-400">No documents uploaded yet.</p>
        )}
      </ul>

      <div className="flex flex-wrap items-end gap-3 rounded border border-zinc-200 p-4 dark:border-zinc-800">
        <label className="flex flex-col gap-1 text-sm">
          Type
          <select
            className="rounded border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900"
            value={documentType}
            onChange={(e) => setDocumentType(e.target.value)}
          >
            {DOCUMENT_TYPES.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Expiry date (optional)
          <input
            type="date"
            className="rounded border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900"
            value={expiryDate}
            onChange={(e) => setExpiryDate(e.target.value)}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          File
          <input ref={fileInputRef} type="file" />
        </label>
        <button
          type="button"
          onClick={handleUpload}
          disabled={uploading}
          className="rounded bg-zinc-900 px-4 py-2 text-sm text-white disabled:opacity-50 dark:bg-zinc-50 dark:text-zinc-900"
        >
          {uploading ? "Uploading…" : "Upload"}
        </button>
      </div>
      {error && <p className="text-sm text-red-600">{error}</p>}
    </section>
  );
}
