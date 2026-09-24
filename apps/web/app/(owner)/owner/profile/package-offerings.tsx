import { ownerPackages } from "@/app/(public)/pricing/data";
import type { OwnerPackage } from "@/lib/types";

import styles from "./package-offerings.module.css";

const TIER_INDEX: Record<OwnerPackage, number> = {
  starter: 0,
  managed: 1,
  full_care: 2,
  complete: 3,
};

export function PackageOfferings({ package: pkg }: { package: OwnerPackage }) {
  const index = TIER_INDEX[pkg];
  const included = ownerPackages.rows.filter((row) => row.values[index] === "included");
  const addOns = ownerPackages.rows.filter((row) => row.values[index] === "addon");

  return (
    <div className={styles.wrapper}>
      <p className={styles.summary}>
        <strong>{ownerPackages.tiers[index]}</strong> — {ownerPackages.positioning[index]}.{" "}
        {ownerPackages.billing?.[index]}.
      </p>
      <div className={styles.columns}>
        <div>
          <h3 className={styles.heading}>Included in your plan</h3>
          <ul className={styles.list}>
            {included.map((row) => (
              <li key={row.label} className={styles.included}>
                {row.label}
              </li>
            ))}
          </ul>
        </div>
        {addOns.length > 0 && (
          <div>
            <h3 className={styles.heading}>Available as an add-on</h3>
            <ul className={styles.list}>
              {addOns.map((row) => (
                <li key={row.label} className={styles.addon}>
                  {row.label}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
