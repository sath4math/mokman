"use client";

import { useEffect, useState } from "react";

import { flushPending } from "@/lib/offline-queue";

import styles from "./field-pwa-client.module.css";

export function FieldPwaClient() {
  const [pendingCount, setPendingCount] = useState(0);

  useEffect(() => {
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/field-sw.js", { scope: "/field/" }).catch(() => {});
    }

    async function flush() {
      try {
        const { remaining } = await flushPending();
        setPendingCount(remaining);
      } catch {
        // IndexedDB unavailable (e.g. private browsing) — nothing to flush.
      }
    }

    flush();
    window.addEventListener("online", flush);
    return () => window.removeEventListener("online", flush);
  }, []);

  if (pendingCount === 0) return null;

  return (
    <div className={styles.banner}>
      {pendingCount} action{pendingCount === 1 ? "" : "s"} queued — will sync when back online.
    </div>
  );
}
