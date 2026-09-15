import type { Cell, PackageTable } from "./data";

const CELL_LABEL: Record<Cell, string> = {
  included: "✓",
  addon: "Add-on",
  none: "—",
};

const CELL_CLASS: Record<Cell, string> = {
  included: "text-emerald-600 dark:text-emerald-400",
  addon: "text-amber-600 dark:text-amber-400",
  none: "text-zinc-400 dark:text-zinc-600",
};

export function PackageTableView({ table, title }: { table: PackageTable; title: string }) {
  return (
    <div className="overflow-x-auto">
      <h2 className="mb-4 text-xl font-semibold">{title}</h2>
      <table className="w-full min-w-[640px] border-collapse text-sm">
        <thead>
          <tr>
            <th className="border-b border-zinc-200 px-3 py-2 text-left dark:border-zinc-800" />
            {table.tiers.map((tier, i) => (
              <th key={tier} className="border-b border-zinc-200 px-3 py-2 text-left dark:border-zinc-800">
                <div className="font-semibold">{tier}</div>
                <div className="mt-1 text-xs font-normal text-zinc-500 dark:text-zinc-400">
                  {table.positioning[i]}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {table.rows.map((row) => (
            <tr key={row.label} className="border-b border-zinc-100 dark:border-zinc-900">
              <td className="px-3 py-2 text-zinc-700 dark:text-zinc-300">{row.label}</td>
              {row.values.map((value, i) => (
                <td key={i} className={`px-3 py-2 ${CELL_CLASS[value]}`}>
                  {CELL_LABEL[value]}
                </td>
              ))}
            </tr>
          ))}
          {table.billing && (
            <tr>
              <td className="px-3 py-3 font-medium">Billing</td>
              {table.billing.map((b, i) => (
                <td key={i} className="px-3 py-3 text-xs text-zinc-600 dark:text-zinc-400">
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
