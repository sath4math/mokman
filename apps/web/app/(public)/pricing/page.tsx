import { addOns, ownerPackages, tenantPackages } from "./data";
import { PackageTableView } from "./package-table";

export default function PricingPage() {
  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-16 px-6 py-16">
      <div>
        <h1 className="text-3xl font-semibold">Pricing</h1>
        <p className="mt-2 text-zinc-600 dark:text-zinc-400">
          Owner and Tenant packages, side by side.
        </p>
      </div>

      <PackageTableView table={ownerPackages} title="Owner Packages" />
      <PackageTableView table={tenantPackages} title="Tenant Packages" />

      <div>
        <h2 className="mb-4 text-xl font-semibold">Standalone Service Add-Ons</h2>
        <p className="mb-3 text-sm text-zinc-600 dark:text-zinc-400">
          Available regardless of package.
        </p>
        <ul className="grid grid-cols-1 gap-2 sm:grid-cols-2">
          {addOns.map((addOn) => (
            <li
              key={addOn}
              className="rounded border border-zinc-200 px-4 py-2 text-sm dark:border-zinc-800"
            >
              {addOn}
            </li>
          ))}
        </ul>
      </div>
    </main>
  );
}
