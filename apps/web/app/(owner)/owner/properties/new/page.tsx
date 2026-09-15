"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import ui from "@/styles/ui.module.css";

import styles from "./new-property.module.css";

export default function NewPropertyPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    category: "residential",
    name: "",
    address_line: "",
    city: "",
    state: "",
    postal_code: "",
    area_sqft: "",
    num_floors: "",
    num_units: "",
    amenities: "",
    furnishing_status: "unfurnished",
  });
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function set(key: keyof typeof form, value: string) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const body = {
        category: form.category,
        name: form.name,
        address_line: form.address_line,
        city: form.city,
        state: form.state,
        postal_code: form.postal_code,
        area_sqft: form.area_sqft ? Number(form.area_sqft) : null,
        num_floors: form.num_floors ? Number(form.num_floors) : null,
        num_units: form.num_units ? Number(form.num_units) : null,
        amenities: form.amenities
          ? form.amenities.split(",").map((a) => a.trim()).filter(Boolean)
          : null,
        furnishing_status: form.furnishing_status,
      };
      const response = await fetch("/api/backend/properties", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Failed to create property");
        return;
      }
      router.push(`/owner/properties/${data.id}`);
      router.refresh();
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className={styles.main}>
      <h1 className={styles.title}>Add Property</h1>
      <form onSubmit={handleSubmit} className={styles.form}>
        <label className={ui.field}>
          Category
          <select
            className={ui.select}
            value={form.category}
            onChange={(e) => set("category", e.target.value)}
          >
            <option value="residential">Residential</option>
            <option value="commercial">Commercial</option>
            <option value="industrial">Industrial</option>
            <option value="land">Land</option>
          </select>
        </label>
        <label className={ui.field}>
          Property name
          <input
            required
            className={ui.input}
            value={form.name}
            onChange={(e) => set("name", e.target.value)}
          />
        </label>
        <label className={ui.field}>
          Address
          <input
            required
            className={ui.input}
            value={form.address_line}
            onChange={(e) => set("address_line", e.target.value)}
          />
        </label>
        <div className={styles.row3}>
          <label className={ui.field}>
            City
            <input
              required
              className={ui.input}
              value={form.city}
              onChange={(e) => set("city", e.target.value)}
            />
          </label>
          <label className={ui.field}>
            State
            <input
              required
              className={ui.input}
              value={form.state}
              onChange={(e) => set("state", e.target.value)}
            />
          </label>
          <label className={ui.field}>
            Postal code
            <input
              required
              className={ui.input}
              value={form.postal_code}
              onChange={(e) => set("postal_code", e.target.value)}
            />
          </label>
        </div>
        <div className={styles.row3}>
          <label className={ui.field}>
            Area (sqft)
            <input
              type="number"
              className={ui.input}
              value={form.area_sqft}
              onChange={(e) => set("area_sqft", e.target.value)}
            />
          </label>
          <label className={ui.field}>
            Floors
            <input
              type="number"
              className={ui.input}
              value={form.num_floors}
              onChange={(e) => set("num_floors", e.target.value)}
            />
          </label>
          <label className={ui.field}>
            Units
            <input
              type="number"
              className={ui.input}
              value={form.num_units}
              onChange={(e) => set("num_units", e.target.value)}
            />
          </label>
        </div>
        <label className={ui.field}>
          Amenities (comma-separated)
          <input
            className={ui.input}
            placeholder="parking, lift, gym"
            value={form.amenities}
            onChange={(e) => set("amenities", e.target.value)}
          />
        </label>
        <label className={ui.field}>
          Furnishing
          <select
            className={ui.select}
            value={form.furnishing_status}
            onChange={(e) => set("furnishing_status", e.target.value)}
          >
            <option value="unfurnished">Unfurnished</option>
            <option value="semi">Semi-furnished</option>
            <option value="full">Fully furnished</option>
          </select>
        </label>
        {error && <p className={ui.errorText}>{error}</p>}
        <button type="submit" disabled={submitting} className={`${ui.btnPrimary} ${styles.submitButton}`}>
          {submitting ? "Creating…" : "Create property"}
        </button>
      </form>
    </main>
  );
}
