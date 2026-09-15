import Link from "next/link";

export default function PublicLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <header className="flex items-center justify-between border-b border-zinc-200 px-6 py-4 dark:border-zinc-800">
        <Link href="/" className="text-lg font-semibold">
          Mokman
        </Link>
        <nav className="flex items-center gap-6 text-sm">
          <Link href="/pricing" className="hover:underline">
            Pricing
          </Link>
          <Link href="/login" className="hover:underline">
            Log in
          </Link>
          <Link
            href="/register"
            className="rounded bg-zinc-900 px-4 py-2 text-white dark:bg-zinc-50 dark:text-zinc-900"
          >
            Sign up
          </Link>
        </nav>
      </header>
      <div className="flex flex-1 flex-col">{children}</div>
      <footer className="border-t border-zinc-200 px-6 py-8 text-sm text-zinc-600 dark:border-zinc-800 dark:text-zinc-400">
        © {new Date().getFullYear()} Mokman. Property Operating System.
      </footer>
    </>
  );
}
