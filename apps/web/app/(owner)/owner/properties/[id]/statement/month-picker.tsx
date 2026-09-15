"use client";

import { useRouter } from "next/navigation";

import ui from "@/styles/ui.module.css";

export function MonthPicker({ propertyId, month }: { propertyId: string; month: string }) {
  const router = useRouter();

  return (
    <label className={ui.field}>
      Month
      <input
        type="month"
        className={ui.input}
        defaultValue={month}
        onChange={(e) => router.push(`/owner/properties/${propertyId}/statement?month=${e.target.value}`)}
      />
    </label>
  );
}
