import Link from "next/link";

import { IconHouse } from "@/components/icons";

const footerColumns = [
  {
    title: "For Owners",
    links: [
      { label: "List Your Property", href: "/register" },
      { label: "Owner Packages", href: "/pricing" },
      { label: "Why Mokman", href: "/#for-owners" },
    ],
  },
  {
    title: "For Tenants",
    links: [
      { label: "Tenant Packages", href: "/pricing" },
      { label: "Why Mokman", href: "/#for-tenants" },
      { label: "Log in", href: "/login" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "How It Works", href: "/#how-it-works" },
      { label: "Services", href: "/#services" },
    ],
  },
  {
    title: "Legal",
    links: [
      { label: "Terms", href: "/terms" },
      { label: "Privacy", href: "/privacy" },
    ],
  },
];

export default function PublicLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <header className="sticky top-0 z-10 border-b border-zinc-200 bg-white/90 backdrop-blur dark:border-zinc-800 dark:bg-zinc-950/90">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-6 px-6 py-4">
          <Link href="/" className="flex items-center gap-2 text-lg font-semibold text-emerald-700 dark:text-emerald-400">
            <IconHouse className="h-6 w-6" />
            Mokman
          </Link>
          <nav className="hidden items-center gap-6 text-sm font-medium text-zinc-700 dark:text-zinc-300 md:flex">
            <Link href="/#for-owners" className="hover:text-emerald-700 dark:hover:text-emerald-400">
              For Owners
            </Link>
            <Link href="/#for-tenants" className="hover:text-emerald-700 dark:hover:text-emerald-400">
              For Tenants
            </Link>
            <Link href="/#services" className="hover:text-emerald-700 dark:hover:text-emerald-400">
              Services
            </Link>
            <Link href="/pricing" className="hover:text-emerald-700 dark:hover:text-emerald-400">
              Pricing
            </Link>
          </nav>
          <div className="flex items-center gap-4">
            <Link href="/login" className="hidden text-sm font-medium hover:underline sm:inline">
              Log in
            </Link>
            <Link
              href="/register"
              className="rounded-full bg-emerald-600 px-5 py-2 text-sm font-semibold text-white shadow-sm hover:bg-emerald-700"
            >
              List Your Property
            </Link>
          </div>
        </div>
      </header>

      <div className="flex flex-1 flex-col">{children}</div>

      <footer className="border-t border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950">
        <div className="mx-auto grid max-w-6xl grid-cols-2 gap-8 px-6 py-12 sm:grid-cols-4">
          {footerColumns.map((column) => (
            <div key={column.title} className="flex flex-col gap-3">
              <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">{column.title}</h3>
              {column.links.map((link) => (
                <Link
                  key={link.label}
                  href={link.href}
                  className="text-sm text-zinc-600 hover:text-emerald-700 dark:text-zinc-400 dark:hover:text-emerald-400"
                >
                  {link.label}
                </Link>
              ))}
            </div>
          ))}
        </div>
        <div className="mx-auto max-w-6xl border-t border-zinc-200 px-6 py-6 text-sm text-zinc-500 dark:border-zinc-800 dark:text-zinc-500">
          © {new Date().getFullYear()} Mokman. Property Operating System.
        </div>
      </footer>
    </>
  );
}
