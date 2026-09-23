import Link from "next/link";
import { redirect } from "next/navigation";

import { LogoutButton } from "@/components/logout-button";
import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { OwnerProfile } from "@/lib/types";
import ui from "@/styles/ui.module.css";

const STATUS_COPY: Record<"not_started" | "pending" | "rejected", { heading: string; body: string }> = {
  not_started: {
    heading: "Complete your KYC to get started",
    body: "Fill in your details and upload a PAN card or ID proof on your profile page. Once submitted, an admin will review it before the rest of Mokman unlocks.",
  },
  pending: {
    heading: "Your KYC is under review",
    body: "An admin is verifying the details and documents you submitted. You'll get full access as soon as it's approved.",
  },
  rejected: {
    heading: "Your KYC was rejected",
    body: "An admin rejected your submission. Please review your details and documents on your profile page and resubmit.",
  },
};

export default async function OwnerKycPendingPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");
  if (user.role !== "owner") redirect("/");

  const profile = await backendFetch<OwnerProfile>("/owner/profile");
  if (profile?.kyc_status === "verified") redirect("/owner");

  const status = profile?.kyc_status ?? "not_started";
  const copy = STATUS_COPY[status];

  return (
    <main className={ui.containerSm}>
      <div className={ui.flexBetween}>
        <h1>Mokman</h1>
        <LogoutButton />
      </div>
      <div className={`${ui.card} ${ui.flexCol}`}>
        <span className={status === "rejected" ? ui.badgeDanger : ui.badge}>{status.replace(/_/g, " ")}</span>
        <h2>{copy.heading}</h2>
        <p className={ui.mutedText}>{copy.body}</p>
        <Link href="/owner/profile" className={ui.btnPrimary}>
          {profile ? "Review your profile" : "Complete your profile"}
        </Link>
      </div>
    </main>
  );
}
