import { notFound, redirect } from "next/navigation";

import { backendFetch } from "@/lib/backend";
import { getCurrentUser } from "@/lib/current-user";
import type { DocumentRecord, Property } from "@/lib/types";

import { DocumentVault } from "./document-vault";

export default async function PropertyDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const { id } = await params;
  const [property, documents] = await Promise.all([
    backendFetch<Property>(`/properties/${id}`),
    backendFetch<DocumentRecord[]>(`/documents?owner_type=property&owner_id=${id}`),
  ]);

  if (!property) notFound();

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-8 px-6 py-16">
      <div>
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold">{property.name}</h1>
          <span className="text-xs uppercase text-zinc-500">{property.status}</span>
        </div>
        <p className="text-zinc-600 dark:text-zinc-400">
          {property.address_line}, {property.city}, {property.state} {property.postal_code}
        </p>
      </div>

      <section className="grid grid-cols-2 gap-4 rounded border border-zinc-200 p-4 text-sm dark:border-zinc-800 sm:grid-cols-4">
        <div>
          <div className="text-zinc-500">Category</div>
          <div>{property.category}</div>
        </div>
        <div>
          <div className="text-zinc-500">Area</div>
          <div>{property.area_sqft ? `${property.area_sqft} sqft` : "—"}</div>
        </div>
        <div>
          <div className="text-zinc-500">Floors</div>
          <div>{property.num_floors ?? "—"}</div>
        </div>
        <div>
          <div className="text-zinc-500">Units</div>
          <div>{property.num_units ?? "—"}</div>
        </div>
        <div className="col-span-2">
          <div className="text-zinc-500">Amenities</div>
          <div>{property.amenities?.join(", ") || "—"}</div>
        </div>
        <div>
          <div className="text-zinc-500">Furnishing</div>
          <div>{property.furnishing_status ?? "—"}</div>
        </div>
      </section>

      <DocumentVault propertyId={property.id} initialDocuments={documents ?? []} />
    </main>
  );
}
