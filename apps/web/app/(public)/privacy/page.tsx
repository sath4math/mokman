import Link from "next/link";

export default function PrivacyPage() {
  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-4 px-6 py-16">
      <h1 className="text-2xl font-semibold">Privacy Policy</h1>
      <p className="text-zinc-600 dark:text-zinc-400">
        Mokman is in active development. A full Privacy Policy describing exactly what data we
        collect and how it&apos;s used will be published here before the platform is opened to
        the public. Today, the platform already encrypts KYC and financial data at rest and logs
        access to it — see our{" "}
        <Link href="/#for-owners" className="underline">
          Trust &amp; Compliance
        </Link>{" "}
        section for details.
      </p>
    </main>
  );
}
