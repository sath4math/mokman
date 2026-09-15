import { redirect } from "next/navigation";

import { RoleDashboard } from "@/components/role-dashboard";
import { getCurrentUser } from "@/lib/current-user";
import { ROLE_FEATURES } from "@/lib/role-features";

export default async function TenantHomePage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  return <RoleDashboard user={user} title="Tenant home" features={ROLE_FEATURES.tenant} />;
}
