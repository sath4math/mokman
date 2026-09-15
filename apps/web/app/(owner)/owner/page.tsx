import { redirect } from "next/navigation";

import { RoleDashboard } from "@/components/role-dashboard";
import { getCurrentUser } from "@/lib/current-user";
import { ROLE_FEATURES } from "@/lib/role-features";

export default async function OwnerDashboardPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  return <RoleDashboard user={user} title="Owner dashboard" features={ROLE_FEATURES.owner} />;
}
