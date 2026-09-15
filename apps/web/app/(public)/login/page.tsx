"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState, type FormEvent } from "react";

import ui from "@/styles/ui.module.css";

import formStyles from "../auth-form.module.css";

const ROLE_HOME: Record<string, string> = {
  owner: "/owner",
  tenant: "/tenant",
  field_staff: "/field",
  admin: "/admin",
};

export default function LoginPage() {
  return (
    <Suspense>
      <LoginForm />
    </Suspense>
  );
}

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Login failed");
        return;
      }
      const next = searchParams.get("next");
      router.push(next ?? ROLE_HOME[data.role] ?? "/");
      router.refresh();
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className={formStyles.main}>
      <h1 className={formStyles.title}>Log in</h1>
      <form onSubmit={handleSubmit} className={formStyles.form}>
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
            autoComplete="current-password"
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
          {submitting ? "Logging in…" : "Log in"}
        </button>
      </form>
      <p className={formStyles.footer}>
        New here?{" "}
        <Link href="/register" className={ui.linkPrimary}>
          Create an account
        </Link>
      </p>
    </main>
  );
}
