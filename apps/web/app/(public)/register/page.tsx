"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import ui from "@/styles/ui.module.css";

import formStyles from "../auth-form.module.css";

const ROLE_HOME: Record<string, string> = {
  owner: "/owner",
  tenant: "/tenant",
};

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"owner" | "tenant">("owner");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ full_name: fullName, email, password, role }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Registration failed");
        return;
      }
      router.push(ROLE_HOME[data.role] ?? "/");
      router.refresh();
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className={formStyles.main}>
      <h1 className={formStyles.title}>Create an account</h1>
      <form onSubmit={handleSubmit} className={formStyles.form}>
        <label className={ui.field}>
          I am a
          <select
            value={role}
            onChange={(event) => setRole(event.target.value as "owner" | "tenant")}
            className={ui.select}
          >
            <option value="owner">Property Owner</option>
            <option value="tenant">Tenant</option>
          </select>
        </label>
        <label className={ui.field}>
          Full name
          <input
            type="text"
            required
            autoComplete="name"
            value={fullName}
            onChange={(event) => setFullName(event.target.value)}
            className={ui.input}
          />
        </label>
        <label className={ui.field}>
          Email
          <input
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className={ui.input}
          />
        </label>
        <label className={ui.field}>
          Password
          <input
            type="password"
            required
            minLength={8}
            autoComplete="new-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className={ui.input}
          />
        </label>
        {error && <p className={ui.errorText}>{error}</p>}
        <button
          type="submit"
          disabled={submitting}
          className={`${ui.btnPrimary} ${formStyles.submitButton}`}
        >
          {submitting ? "Creating account…" : "Create account"}
        </button>
      </form>
      <p className={formStyles.footer}>
        Already have an account?{" "}
        <Link href="/login" className={ui.linkPrimary}>
          Log in
        </Link>
      </p>
    </main>
  );
}
