import { requireVerifiedOwner } from "@/lib/current-user";

import { NewLeaseForm } from "./new-lease-form";

export default async function NewLeasePage() {
  await requireVerifiedOwner();
  return <NewLeaseForm />;
}
