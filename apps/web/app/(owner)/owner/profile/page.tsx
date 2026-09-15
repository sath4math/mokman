import { redirect } from "next/navigation";

import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { AuthorizedRepresentative, OwnerProfile } from "@/lib/types";

import { ProfileForm } from "./profile-form";

export default async function OwnerProfilePage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const [profile, representatives] = await Promise.all([
    backendFetch<OwnerProfile>("/owner/profile"),
    backendFetch<AuthorizedRepresentative[]>("/owner/profile/representatives"),
  ]);

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-8 px-6 py-16">
      <h1 className="text-2xl font-semibold">Owner Profile</h1>
      <ProfileForm initialProfile={profile} initialRepresentatives={representatives ?? []} />
    </main>
  );
}
