import { addOns, ownerPackages, tenantPackages } from "./data";
import { PackageTableView } from "./package-table";
import styles from "./pricing.module.css";

export default function PricingPage() {
  return (
    <main className={styles.main}>
      <div className={styles.banner}>
        <div>
          <h1 className={styles.title}>Pricing</h1>
          <p className={styles.subtitle}>Owner and Tenant packages, side by side.</p>
        </div>
      </div>

      <PackageTableView table={ownerPackages} title="Owner Packages" />
      <PackageTableView table={tenantPackages} title="Tenant Packages" />

      <div>
        <h2 className={styles.addOnsTitle}>Standalone Service Add-Ons</h2>
        <p className={styles.addOnsSubtitle}>Available regardless of package.</p>
        <ul className={styles.addOnsGrid}>
          {addOns.map((addOn) => (
            <li key={addOn} className={styles.addOnItem}>
              {addOn}
            </li>
          ))}
        </ul>
      </div>
    </main>
  );
}
