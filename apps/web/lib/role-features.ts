// Presentational only — sourced from docs/Mokman_Product_Feature_Specification.md
// Sections 4-7. Nothing here is backed by live data yet.

export const ROLE_FEATURES: Record<string, string[]> = {
  owner: [
    "Portfolio dashboard: occupancy, rent collected, pending approvals",
    "Property list & Digital Property Passport",
    "Tenant list & lease summaries",
    "Financial statements & downloadable reports",
    "Maintenance tickets & inspection reports",
    "Document vault with expiry tracking",
    "Insurance, legal notices & renovation projects",
    "AI property assistant (roadmap)",
  ],
  tenant: [
    "Home: lease status, next rent due, announcements",
    "Rent payment (UPI/card/bank transfer) & digital receipts",
    "Raise and track maintenance requests",
    "Lease agreement & move-in/move-out documents",
    "Messages: chat with Mokman support",
    "Profile: KYC status, occupants, emergency contact",
  ],
  field_staff: [
    "My Jobs: assigned work orders sorted by priority",
    "Check-in/check-out with GPS timestamp",
    "Before/after photo and video capture",
    "Schedule: calendar of upcoming assignments",
    "Materials: request and usage logging",
    "Offline mode with background sync (roadmap)",
  ],
  admin: [
    "Platform-wide KPIs: occupancy, collections, SLA compliance",
    "Owner, property, tenant & lease management",
    "Finance: ledger, invoices, payout processing",
    "Operations: ticket queue & SLA monitoring",
    "Workforce & vendor management",
    "Configurable reports & role-based access control",
  ],
};

export const ROLE_LABEL: Record<string, string> = {
  owner: "Owners",
  tenant: "Tenants",
  field_staff: "Field Staff",
  admin: "Admins",
};
