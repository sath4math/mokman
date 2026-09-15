// Sourced from docs/Mokman_Product_Feature_Specification.md, Section 3.

export type Cell = "included" | "addon" | "none";

export interface PackageTable {
  tiers: string[];
  positioning: string[];
  billing?: string[];
  rows: { label: string; values: Cell[] }[];
}

const I: Cell = "included";
const A: Cell = "addon";
const N: Cell = "none";

export const ownerPackages: PackageTable = {
  tiers: ["Starter", "Managed", "Full Care", "Complete"],
  positioning: [
    "Self-serve digital record-keeping",
    "Rent handled for you",
    "Full operations handled for you",
    "Everything, including in-house workforce & intelligence",
  ],
  billing: [
    "Free or low flat annual fee",
    "% of monthly rent or flat monthly fee",
    "Higher % of rent or premium flat fee",
    "Premium subscription, highest tier",
  ],
  rows: [
    { label: "Property registration & Digital Property Passport", values: [I, I, I, I] },
    { label: "Document vault & expiry alerts", values: [I, I, I, I] },
    { label: "Owner dashboard & activity history", values: [I, I, I, I] },
    { label: "Tenant verification & KYC", values: [A, I, I, I] },
    { label: "Lease creation & e-signature", values: [A, I, I, I] },
    { label: "Move-in / move-out management", values: [A, I, I, I] },
    { label: "Rent collection & reconciliation", values: [N, I, I, I] },
    { label: "Security deposit management", values: [N, I, I, I] },
    { label: "Owner financial statements & reports", values: [N, I, I, I] },
    { label: "Maintenance ticketing & vendor coordination", values: [N, A, I, I] },
    { label: "Scheduled inspections", values: [N, A, I, I] },
    { label: "Preventive maintenance scheduling", values: [N, N, I, I] },
    { label: "Utility & society/government coordination", values: [N, N, I, I] },
    { label: "End-to-end managed service delivery", values: [N, N, A, I] },
    { label: "In-house workforce priority access", values: [N, N, N, I] },
    { label: "Insurance management", values: [A, A, A, I] },
    { label: "Legal & notice support", values: [A, A, I, I] },
    { label: "Asset & renovation project management", values: [N, N, A, I] },
    { label: "AI property assistant & health score", values: [N, N, A, I] },
    { label: "Predictive maintenance & financial intelligence", values: [N, N, N, I] },
    { label: "Investment insights & portfolio analytics", values: [N, N, A, I] },
    { label: "NRI-specific coordination", values: [A, A, A, I] },
    { label: "Sale/exit support", values: [A, A, A, I] },
  ],
};

export const tenantPackages: PackageTable = {
  tiers: ["Standard", "Verified", "Priority"],
  positioning: [
    "Free account for any tenant in a Mokman-managed property",
    "Adds a verified badge for faster approval on future applications",
    "Premium support and faster service turnaround",
  ],
  rows: [
    { label: "Tenant portal & app access", values: [I, I, I] },
    { label: "Rent payment & digital receipts", values: [I, I, I] },
    { label: "Lease document access", values: [I, I, I] },
    { label: "Maintenance request submission", values: [I, I, I] },
    { label: "Standard-queue maintenance response", values: [I, I, N] },
    { label: "Priority-queue maintenance response", values: [N, N, I] },
    { label: "Identity/employment/reference verification badge", values: [N, I, I] },
    { label: "Faster application approval on future Mokman listings", values: [N, I, I] },
    { label: "Dedicated support line", values: [N, N, I] },
    { label: "Move-in/move-out concierge scheduling", values: [N, N, I] },
    { label: "Early access to AI assistant", values: [N, N, I] },
  ],
};

export const addOns = [
  "Tenant verification (one-off, per tenancy)",
  "Property inspection (one-off, per visit)",
  "Insurance policy setup and claim assistance",
  "Legal notice drafting and eviction support",
  "Renovation project management",
  "Investment/portfolio consultation",
];
