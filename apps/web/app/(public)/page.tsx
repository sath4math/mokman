import Link from "next/link";

export default function HomePage() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-6 px-6 py-24 text-center">
      <h1 className="text-4xl font-semibold tracking-tight">Mokman</h1>
      <p className="max-w-md text-lg text-zinc-600 dark:text-zinc-400">
        A Property Operating System. Hand over the work, keep the ownership —
        or get a home that&apos;s actually looked after.
      </p>
      <div className="flex flex-wrap items-center justify-center gap-4">
        <Link
          href="/register"
          className="rounded bg-zinc-900 px-5 py-3 text-white dark:bg-zinc-50 dark:text-zinc-900"
        >
          List Your Property
        </Link>
        <Link
          href="/pricing"
          className="rounded border border-zinc-300 px-5 py-3 dark:border-zinc-700"
        >
          See Pricing
        </Link>
      </div>
    </main>
  );
}
