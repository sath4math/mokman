"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

const inputClass = "rounded border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900";

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
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-8 px-6 py-16">
      <h1 className="text-2xl font-semibold">Add Property</h1>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <label className="flex flex-col gap-1 text-sm">
          Category
          <select
            className={inputClass}
            value={form.category}
            onChange={(e) => set("category", e.target.value)}
          >
            <option value="residential">Residential</option>
            <option value="commercial">Commercial</option>
            <option value="industrial">Industrial</option>
            <option value="land">Land</option>
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Property name
          <input
            required
            className={inputClass}
            value={form.name}
            onChange={(e) => set("name", e.target.value)}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Address
          <input
            required
            className={inputClass}
            value={form.address_line}
            onChange={(e) => set("address_line", e.target.value)}
          />
        </label>
        <div className="grid grid-cols-3 gap-4">
          <label className="flex flex-col gap-1 text-sm">
            City
            <input
              required
              className={inputClass}
              value={form.city}
              onChange={(e) => set("city", e.target.value)}
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            State
            <input
              required
              className={inputClass}
              value={form.state}
              onChange={(e) => set("state", e.target.value)}
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            Postal code
            <input
              required
              className={inputClass}
              value={form.postal_code}
              onChange={(e) => set("postal_code", e.target.value)}
            />
          </label>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <label className="flex flex-col gap-1 text-sm">
            Area (sqft)
            <input
              type="number"
              className={inputClass}
              value={form.area_sqft}
              onChange={(e) => set("area_sqft", e.target.value)}
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            Floors
            <input
              type="number"
              className={inputClass}
              value={form.num_floors}
              onChange={(e) => set("num_floors", e.target.value)}
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            Units
            <input
              type="number"
              className={inputClass}
              value={form.num_units}
              onChange={(e) => set("num_units", e.target.value)}
            />
          </label>
        </div>
        <label className="flex flex-col gap-1 text-sm">
          Amenities (comma-separated)
          <input
            className={inputClass}
            placeholder="parking, lift, gym"
            value={form.amenities}
            onChange={(e) => set("amenities", e.target.value)}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Furnishing
          <select
            className={inputClass}
            value={form.furnishing_status}
            onChange={(e) => set("furnishing_status", e.target.value)}
          >
            <option value="unfurnished">Unfurnished</option>
            <option value="semi">Semi-furnished</option>
            <option value="full">Fully furnished</option>
          </select>
        </label>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          type="submit"
          disabled={submitting}
          className="w-fit rounded bg-zinc-900 px-5 py-2 text-white disabled:opacity-50 dark:bg-zinc-50 dark:text-zinc-900"
        >
          {submitting ? "Creating…" : "Create property"}
        </button>
      </form>
    </main>
  );
}
