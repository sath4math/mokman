"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import styles from "./logout-button.module.css";

export function LogoutButton() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function handleLogout() {
    setLoading(true);
    await fetch("/api/auth/logout", { method: "POST" });
    router.push("/");
    router.refresh();
  }

  return (
    <button
      type="button"
      onClick={handleLogout}
      disabled={loading}
      className={styles.button}
    >
      {loading ? "Logging out…" : "Log out"}
    </button>
  );
}
