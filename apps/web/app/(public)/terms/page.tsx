import styles from "../legal-page.module.css";

export default function TermsPage() {
  return (
    <main className={styles.main}>
      <h1 className={styles.title}>Terms of Service</h1>
      <p className={styles.body}>
        Mokman is in active development. Formal Terms of Service will be published here before
        the platform is opened to the public. If you have questions in the meantime, please
        contact us directly.
      </p>
    </main>
  );
}
