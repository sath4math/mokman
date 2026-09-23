import { redirect } from "next/navigation";

import { NewPropertyForm } from "@/app/(owner)/owner/properties/new/new-property-form";
import { getCurrentUser } from "@/lib/current-user";

export default async function AdminNewPropertyPage({
  params,
}: {
  params: Promise<{ ownerId: string }>;
}) {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const { ownerId } = await params;
  return <NewPropertyForm onBehalfOfOwnerId={ownerId} />;
}
