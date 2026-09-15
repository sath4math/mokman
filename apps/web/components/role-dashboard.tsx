import { LogoutButton } from "@/components/logout-button";
import type { CurrentUser } from "@/lib/session";

import styles from "./role-dashboard.module.css";

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
    <main className={styles.main}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Welcome, {user.full_name ?? user.email}</h1>
          <p className={styles.subtitle}>{title}</p>
        </div>
        <LogoutButton />
      </div>
      <section>
        <h2 className={styles.sectionTitle}>Available features</h2>
        <ul className={styles.list}>
          {features.map((feature) => (
            <li key={feature} className={styles.listItem}>
              {feature}
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
