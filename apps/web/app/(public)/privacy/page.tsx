import Link from "next/link";

import ui from "@/styles/ui.module.css";

import styles from "../legal-page.module.css";

export default function PrivacyPage() {
  return (
    <main className={styles.main}>
      <h1 className={styles.title}>Privacy Policy</h1>
      <p className={styles.body}>
        Mokman is in active development. A full Privacy Policy describing exactly what data we
        collect and how it&apos;s used will be published here before the platform is opened to
        the public. Today, the platform already encrypts KYC and financial data at rest and logs
        access to it — see our{" "}
        <Link href="/#for-owners" className={ui.link}>
          Trust &amp; Compliance
        </Link>{" "}
        section for details.
      </p>
    </main>
  );
}
