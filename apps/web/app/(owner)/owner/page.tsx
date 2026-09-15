import Link from "next/link";
import { redirect } from "next/navigation";

import { LogoutButton } from "@/components/logout-button";
import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { OwnerProfile, Property } from "@/lib/types";

export default async function OwnerDashboardPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const [profile, properties] = await Promise.all([
    backendFetch<OwnerProfile>("/owner/profile"),
    backendFetch<Property[]>("/properties"),
  ]);

  return (
    <main className="flex flex-1 flex-col gap-8 px-6 py-16">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Welcome, {user.full_name ?? user.email}</h1>
          <p className="text-zinc-600 dark:text-zinc-400">Owner dashboard</p>
        </div>
        <LogoutButton />
      </div>

      <section className="flex items-center justify-between rounded border border-zinc-200 px-4 py-3 dark:border-zinc-800">
        <p className="text-sm">
          KYC status: <span className="font-medium">{profile?.kyc_status ?? "not started"}</span>
        </p>
        <Link href="/owner/profile" className="text-sm underline">
          {profile ? "Edit profile" : "Complete your profile"}
        </Link>
      </section>

      <section className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-medium">Your properties</h2>
          <Link
            href="/owner/properties/new"
            className="rounded bg-zinc-900 px-4 py-2 text-sm text-white dark:bg-zinc-50 dark:text-zinc-900"
          >
            Add Property
          </Link>
        </div>

        {properties && properties.length > 0 ? (
          <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {properties.map((property) => (
              <li key={property.id}>
                <Link
                  href={`/owner/properties/${property.id}`}
                  className="block rounded border border-zinc-200 px-4 py-3 hover:border-zinc-400 dark:border-zinc-800 dark:hover:border-zinc-600"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{property.name}</span>
                    <span className="text-xs uppercase text-zinc-500">{property.status}</span>
                  </div>
                  <p className="text-sm text-zinc-600 dark:text-zinc-400">
                    {property.address_line}, {property.city}
                  </p>
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            No properties yet — add your first one.
          </p>
        )}
      </section>
    </main>
  );
}
