import { requireVerifiedOwner } from "@/lib/current-user";

import { NewPropertyForm } from "./new-property-form";

export default async function NewPropertyPage() {
  await requireVerifiedOwner();
  return <NewPropertyForm />;
}
