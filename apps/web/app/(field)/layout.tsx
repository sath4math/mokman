import type { Metadata } from "next";

import { FieldPwaClient } from "@/components/field-pwa-client";

export const metadata: Metadata = {
  manifest: "/field-manifest.json",
};

export default function FieldLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <FieldPwaClient />
      {children}
    </>
  );
}
