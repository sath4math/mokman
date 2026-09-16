import Link from "next/link";

import ui from "@/styles/ui.module.css";

import styles from "./layout.module.css";

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
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <Link href="/" className={styles.logo}>
            <img src="/mokman-logo.png" alt="" className={styles.logoMark} />
            Mokman
          </Link>
          <nav className={styles.nav}>
            <Link href="/#for-owners" className={styles.navLink}>
              For Owners
            </Link>
            <Link href="/#for-tenants" className={styles.navLink}>
              For Tenants
            </Link>
            <Link href="/#services" className={styles.navLink}>
              Services
            </Link>
            <Link href="/pricing" className={styles.navLink}>
              Pricing
            </Link>
          </nav>
          <div className={styles.utilityRow}>
            <Link href="/login" className={styles.loginLink}>
              Log in
            </Link>
            <Link href="/register" className={`${ui.btnPrimary} ${ui.btnSmall}`}>
              List Your Property
            </Link>
          </div>
        </div>
      </header>

      <div className={styles.body}>{children}</div>

      <footer className={styles.footer}>
        <div className={styles.footerGrid}>
          {footerColumns.map((column) => (
            <div key={column.title} className={styles.footerColumn}>
              <h3 className={styles.footerHeading}>{column.title}</h3>
              {column.links.map((link) => (
                <Link key={link.label} href={link.href} className={styles.footerLink}>
                  {link.label}
                </Link>
              ))}
            </div>
          ))}
        </div>
        <div className={styles.footerBottom}>
          © {new Date().getFullYear()} Mokman. Property Operating System.
        </div>
      </footer>
    </>
  );
}
