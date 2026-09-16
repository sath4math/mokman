import Link from "next/link";
import { redirect } from "next/navigation";

import { RoleDashboard } from "@/components/role-dashboard";
import { getCurrentUser } from "@/lib/current-user";
import { ROLE_FEATURES } from "@/lib/role-features";
import ui from "@/styles/ui.module.css";

import styles from "./admin-page.module.css";

export default async function AdminOverviewPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  return (
    <>
      <RoleDashboard user={user} title="Admin portal" features={ROLE_FEATURES.admin} />
      <p className={styles.linkRow}>
        <Link href="/admin/expenses" className={ui.linkPrimary}>
          Manage expenses →
        </Link>
      </p>
      <p className={styles.linkRow}>
        <Link href="/admin/tickets" className={ui.linkPrimary}>
          Manage tickets →
        </Link>
      </p>
      <p className={styles.linkRow}>
        <Link href="/admin/vendors" className={ui.linkPrimary}>
          Manage vendors →
        </Link>
      </p>
      <p className={styles.linkRow}>
        <Link href="/admin/checklist-templates" className={ui.linkPrimary}>
          Manage checklist templates →
        </Link>
      </p>
      <p className={styles.linkRow}>
        <Link href="/admin/service-categories" className={ui.linkPrimary}>
          Manage service categories →
        </Link>
      </p>
      <p className={styles.linkRow}>
        <Link href="/admin/eligibility-rules" className={ui.linkPrimary}>
          Manage eligibility rules →
        </Link>
      </p>
    </>
  );
}
