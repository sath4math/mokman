import { redirect } from "next/navigation";

import { LogoutButton } from "@/components/logout-button";
import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { OwnerProfileAdmin } from "@/lib/types";
import ui from "@/styles/ui.module.css";

import { AdminKycPanel } from "./admin-kyc-panel";
import styles from "./kyc.module.css";

export default async function AdminKycPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const profiles = await backendFetch<OwnerProfileAdmin[]>("/owner/profiles");

  return (
    <main className={styles.main}>
      <div className={ui.flexBetween}>
        <h1 className={styles.title}>Owner KYC</h1>
        <LogoutButton />
      </div>
      <AdminKycPanel initialProfiles={profiles ?? []} />
    </main>
  );
}
