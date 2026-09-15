import type { Cell, PackageTable } from "./data";
import styles from "./pricing.module.css";

const CELL_LABEL: Record<Cell, string> = {
  included: "✓",
  addon: "Add-on",
  none: "—",
};

const CELL_CLASS: Record<Cell, string> = {
  included: styles.cellIncluded,
  addon: styles.cellAddon,
  none: styles.cellNone,
};

export function PackageTableView({ table, title }: { table: PackageTable; title: string }) {
  return (
    <div className={styles.tableWrap}>
      <h2 className={styles.tableTitle}>{title}</h2>
      <table className={styles.table}>
        <thead>
          <tr>
            <th className={styles.th} />
            {table.tiers.map((tier, i) => (
              <th key={tier} className={styles.th}>
                <div className={styles.tierName}>{tier}</div>
                <div className={styles.tierPositioning}>{table.positioning[i]}</div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {table.rows.map((row) => (
            <tr key={row.label} className={styles.row}>
              <td className={styles.rowLabel}>{row.label}</td>
              {row.values.map((value, i) => (
                <td key={i} className={CELL_CLASS[value]}>
                  {CELL_LABEL[value]}
                </td>
              ))}
            </tr>
          ))}
          {table.billing && (
            <tr>
              <td className={styles.billingLabel}>Billing</td>
              {table.billing.map((b, i) => (
                <td key={i} className={styles.billingValue}>
                  {b}
                </td>
              ))}
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
