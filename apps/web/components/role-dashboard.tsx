import { LogoutButton } from "@/components/logout-button";
import type { CurrentUser } from "@/lib/session";

export function RoleDashboard({
  user,
  title,
  features,
}: {
  user: CurrentUser;
  title: string;
  features: string[];
}) {
  return (
    <main className="flex flex-1 flex-col gap-8 px-6 py-16">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">
            Welcome, {user.full_name ?? user.email}
          </h1>
          <p className="text-zinc-600 dark:text-zinc-400">{title}</p>
        </div>
        <LogoutButton />
      </div>
      <section>
        <h2 className="mb-3 text-lg font-medium">Available features</h2>
        <ul className="flex flex-col gap-2">
          {features.map((feature) => (
            <li
              key={feature}
              className="rounded border border-zinc-200 px-4 py-2 text-sm dark:border-zinc-800"
            >
              {feature}
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
