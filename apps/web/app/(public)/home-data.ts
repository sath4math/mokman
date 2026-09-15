export const ownerBenefits = [
  {
    icon: "shield",
    title: "Verified tenants",
    body: "Identity, employment and reference checks before anyone moves in.",
  },
  {
    icon: "wallet",
    title: "Reliable rent collection",
    body: "Digital payments, reconciliation, and clear monthly statements.",
  },
  {
    icon: "wrench",
    title: "End-to-end maintenance",
    body: "From complaint to closure, tracked and coordinated for you.",
  },
  {
    icon: "file",
    title: "Full financial transparency",
    body: "Every rupee in and out, visible in your dashboard at all times.",
  },
] as const;

export const tenantBenefits = [
  {
    icon: "building",
    title: "Verified landlords & properties",
    body: "Every listing on Mokman is backed by a real, managed property record.",
  },
  {
    icon: "file",
    title: "Transparent lease terms",
    body: "Digital lease documents you can read and reference any time.",
  },
  {
    icon: "wrench",
    title: "Fast maintenance response",
    body: "Raise an issue from your phone and track it through to completion.",
  },
  {
    icon: "wallet",
    title: "Digital rent payments",
    body: "Pay rent and get instant digital receipts — no more chasing paperwork.",
  },
] as const;

export const howItWorks = [
  {
    step: "1",
    title: "Register your property",
    body: "Add your property's details, specs, and documents to its Digital Property Passport.",
  },
  {
    step: "2",
    title: "Complete your KYC",
    body: "Owner verification and bank details, done once, kept secure.",
  },
  {
    step: "3",
    title: "Tenant placed & verified",
    body: "Mokman coordinates verification, lease signing, and move-in.",
  },
  {
    step: "4",
    title: "Mokman manages operations",
    body: "Rent, maintenance, inspections and reporting — you stay informed, not overloaded.",
  },
] as const;

export const services = [
  { icon: "clipboard", title: "Tenant Verification", body: "Identity, employment, and reference checks." },
  { icon: "wallet", title: "Rent Collection", body: "Digital collection with automatic reconciliation." },
  { icon: "wrench", title: "Maintenance & Repairs", body: "Ticketing, vendor coordination, and closure tracking." },
  { icon: "building", title: "Inspections", body: "Scheduled and event-triggered property inspections." },
  { icon: "umbrella", title: "Insurance", body: "Policy setup and claim assistance for your property." },
  { icon: "scale", title: "Legal Support", body: "Notice drafting and eviction support when it's needed." },
] as const;

export const trustPoints = [
  "Role-based access with property-level data isolation",
  "Encryption at rest for KYC and financial data",
  "Full audit logging of approvals and document access",
] as const;
