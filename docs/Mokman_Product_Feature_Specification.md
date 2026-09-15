# Mokman — Product Feature Specification

**Purpose of this document:** a build-reference specification covering the public website (landing page, navigation, packages), and the four application surfaces (Owner App, Tenant App, Field Staff App, Admin Portal). Use this alongside the phase-wise development plan for implementation sequencing; this document defines *what each screen and package contains*.

---

## 1. Product Overview

**Mokman** is a Property Operating System. Owners hand over property responsibility to Mokman; Mokman's internal teams use the same system to operate, maintain, and improve the property. It is positioned as an end-to-end operator, not a listings or referral marketplace.

**Primary user types:**
- **Owner** — lists a property with Mokman and consumes services at varying levels of hands-off management.
- **Tenant** — rents a Mokman-managed property and interacts with rent, maintenance, and lease processes digitally.
- **Field Staff** — technicians and inspectors who execute work orders and inspections.
- **Internal Admin/Ops** — Mokman's own team operating the platform, vendors, and workforce.

---

## 2. Public Website

### 2.1 Landing Page Structure

**Header (sticky navigation)** — see Section 2.2.

**Section 1 — Hero**
- Headline + subheadline communicating "we manage your property end-to-end"
- Primary CTA: "List Your Property" (owner path)
- Secondary CTA: "Find a Home" (tenant path) — only if Mokman also surfaces available managed properties to prospective tenants; otherwise replace with "See How It Works"
- Trust indicators: number of properties managed, cities covered, average response time

**Section 2 — For Owners**
- Value proposition: "Hand over the work, keep the ownership"
- Three to four benefit tiles: Verified tenants, Guaranteed rent collection, End-to-end maintenance, Full financial transparency
- CTA: "List Your Property" → property registration flow
- Secondary link: "See Owner Packages" → anchor to pricing section

**Section 3 — For Tenants**
- Value proposition: "A home that's actually looked after"
- Benefit tiles: Verified landlords/properties, Transparent lease terms, Fast maintenance response, Digital rent payments
- CTA: "Browse Managed Properties" or "Learn More" depending on whether public listings exist

**Section 4 — How It Works**
- Step-by-step visual (4–5 steps) covering: Owner registers property → Property assessed & onboarded → Tenant placed & verified → Mokman manages operations → Owner receives reports & payouts

**Section 5 — Packages Preview**
- Condensed comparison of Owner package tiers (see Section 3) with a "Compare all packages" CTA
- Condensed tenant package tiers if tenant-facing paid tiers exist

**Section 6 — Services Showcase**
- Grid of core service categories: Tenant Verification, Rent Collection, Maintenance & Repairs, Inspections, Insurance, Legal Support, Property Investment Insights
- Each tile links to a dedicated service detail page

**Section 7 — Featured/Managed Properties** *(optional, only if the platform surfaces properties publicly)*
- Card grid: photo, rent, bed/bath count, locality, status (Available/Occupied)

**Section 8 — Testimonials**
- Owner and tenant quotes, rotating carousel, with rating stars

**Section 9 — Trust & Compliance**
- Security badges, KYC/verification assurance, data protection statement, insurance-backed guarantees if applicable

**Section 10 — Popular Locations**
- Text link grid of top cities/localities served

**Footer**
- Columns: For Owners (links to each owner service/package), For Tenants (links to tenant resources), Company (About, Careers, Press, Blog), Support (Help Centre, FAQs, Contact, Community), Legal (Terms, Privacy, Refund Policy)
- Social links, app store badges (iOS/Android), copyright line

### 2.2 Header Navigation (Menu Structure)

```
Logo | For Owners ▾ | For Tenants ▾ | Services ▾ | Pricing | About | [List Your Property] | [Log In]
```

**For Owners (dropdown)**
- Why Mokman for Owners
- List Your Property
- Owner Packages
- Owner Dashboard (login-gated)
- Owner FAQs

**For Tenants (dropdown)**
- Why Mokman for Tenants
- Browse Managed Properties *(if applicable)*
- Tenant Verification
- Tenant Dashboard (login-gated)
- Tenant FAQs

**Services (dropdown)**
- Tenant Verification & Compliance
- Rent Collection
- Property Management (Full Management tier)
- Maintenance & Repairs
- Inspections
- Insurance
- Legal & Notices
- Investment & Portfolio Insights
- Renovation & Asset Management

**Pricing** — single page listing Owner and Tenant packages side by side.

**Utility nav (top-right or persistent)**
- Log In (role-aware: routes owner/tenant/staff to correct dashboard)
- List Your Property (primary CTA button)
- Language/region selector, if multi-region

---

## 3. Packages

### 3.1 Owner Packages

| | **Starter** | **Managed** | **Full Care** | **Complete** |
|---|---|---|---|---|
| **Positioning** | Self-serve digital record-keeping | Rent handled for you | Full operations handled for you | Everything, including in-house workforce & intelligence |
| Property registration & Digital Property Passport | ✓ | ✓ | ✓ | ✓ |
| Document vault & expiry alerts | ✓ | ✓ | ✓ | ✓ |
| Owner dashboard & activity history | ✓ | ✓ | ✓ | ✓ |
| Tenant verification & KYC | Add-on | ✓ | ✓ | ✓ |
| Lease creation & e-signature | Add-on | ✓ | ✓ | ✓ |
| Move-in / move-out management | Add-on | ✓ | ✓ | ✓ |
| Rent collection & reconciliation | — | ✓ | ✓ | ✓ |
| Security deposit management | — | ✓ | ✓ | ✓ |
| Owner financial statements & reports | — | ✓ | ✓ | ✓ |
| Maintenance ticketing & vendor coordination | — | Add-on | ✓ | ✓ |
| Scheduled inspections | — | Add-on | ✓ | ✓ |
| Preventive maintenance scheduling | — | — | ✓ | ✓ |
| Utility & society/government coordination | — | — | ✓ | ✓ |
| End-to-end managed service delivery (diagnosis to closure) | — | — | Add-on | ✓ |
| In-house workforce priority access | — | — | — | ✓ |
| Insurance management | Add-on | Add-on | Add-on | ✓ |
| Legal & notice support | Add-on | Add-on | ✓ | ✓ |
| Asset & renovation project management | — | — | Add-on | ✓ |
| AI property assistant & health score | — | — | Add-on | ✓ |
| Predictive maintenance & financial intelligence | — | — | — | ✓ |
| Investment insights & portfolio analytics | — | — | Add-on | ✓ |
| NRI-specific coordination | Add-on | Add-on | Add-on | ✓ |
| Sale/exit support | Add-on | Add-on | Add-on | ✓ |
| **Billing model** | Free or low flat annual fee | % of monthly rent or flat monthly fee | Higher % of rent or premium flat fee | Premium subscription, highest tier |

### 3.2 Tenant Packages

| | **Standard** | **Verified** | **Priority** |
|---|---|---|---|
| **Positioning** | Free account for any tenant in a Mokman-managed property | Adds a verified badge for faster approval on future applications | Premium support and faster service turnaround |
| Tenant portal & app access | ✓ | ✓ | ✓ |
| Rent payment & digital receipts | ✓ | ✓ | ✓ |
| Lease document access | ✓ | ✓ | ✓ |
| Maintenance request submission | ✓ | ✓ | ✓ |
| Standard-queue maintenance response | ✓ | ✓ | — |
| Priority-queue maintenance response | — | — | ✓ |
| Identity/employment/reference verification badge | — | ✓ | ✓ |
| Faster application approval on future Mokman listings | — | ✓ | ✓ |
| Dedicated support line | — | — | ✓ |
| Move-in/move-out concierge scheduling | — | — | ✓ |
| Early access to AI assistant (Q&A on lease/rent/maintenance status) | — | — | ✓ |

### 3.3 Standalone Service Add-Ons (available regardless of package)

- Tenant verification (one-off, per tenancy)
- Property inspection (one-off, per visit)
- Insurance policy setup and claim assistance
- Legal notice drafting and eviction support
- Renovation project management
- Investment/portfolio consultation

---

## 4. Owner App

### 4.1 Navigation (bottom nav or side menu)

```
Dashboard | Properties | Tenants | Finances | Maintenance | Documents | More
```

**Dashboard**
- Portfolio summary: total properties, occupancy rate, this month's rent collected, pending approvals, open maintenance tickets
- Alerts feed: lease expiries, document expiries, overdue rent, inspection due
- Quick actions: Add Property, Approve Pending Item, View Latest Statement

**Properties**
- Property list (card/list view) with status badges (Vacant/Occupied/Under Maintenance)
- Property detail page: Digital Property Passport, structure hierarchy, media gallery, current tenant, lease summary, maintenance history, document list, financial summary, inspection history

**Tenants**
- Tenant list per property
- Tenant profile: verification status, lease terms, payment history, communication log

**Finances**
- Monthly/annual statements
- Income vs. expense breakdown
- Rent collection status per property
- Deposit ledger
- Downloadable reports (PDF/Excel)
- Pending expense approvals

**Maintenance**
- Open/closed tickets list
- Ticket detail: category, priority, assigned vendor/technician, cost estimate, approval action, progress photos, invoice
- Inspection reports
- Preventive maintenance calendar

**Documents**
- Full document vault by property
- Expiry tracker
- Upload/search

**More (menu overflow)**
- Insurance
- Legal & Notices
- Renovation Projects
- Investment Insights
- AI Assistant (chat interface)
- Settings (profile, KYC, bank details, notification preferences, authorised representatives)
- Support

### 4.2 Owner Onboarding Flow
1. Registration (mobile/email) → OTP verification
2. Passwordless login setup
3. KYC (PAN, Aadhaar/passport, bank details)
4. Ownership details (single/joint, percentage, nominee)
5. Add first property (guided form: category → address → specifications → media → documents)
6. Package selection
7. Dashboard landing

---

## 5. Tenant App

### 5.1 Navigation

```
Home | Rent | Maintenance | Documents | Messages | Profile
```

**Home**
- Current property summary, lease status, next rent due date, active maintenance tickets, announcements

**Rent**
- Payment screen (UPI/card/bank transfer), payment history, receipts, upcoming due dates, late-fee notices

**Maintenance**
- Raise complaint (category, description, photo/video, location within unit)
- Track ticket status
- Rate completed work

**Documents**
- Lease agreement, move-in/move-out reports, notices

**Messages**
- Chat with Mokman support
- Broadcast/announcement inbox

**Profile**
- Personal details, KYC status, occupants, vehicles, pets, emergency contact, notification preferences

### 5.2 Tenant Onboarding Flow
1. Registration/verification (via owner invite or self-application)
2. KYC and verification submission
3. Lease review and e-signature
4. Move-in scheduling and digital condition report acknowledgement
5. App dashboard landing

---

## 6. Field Staff App

### 6.1 Navigation

```
My Jobs | Schedule | Materials | Profile
```

**My Jobs**
- Assigned job list (sorted by priority/time), job detail (address, navigation link, checklist, customer contact)
- Check-in/check-out with GPS timestamp
- Before/after photo and video capture
- Completion report and customer signature capture
- Offline mode with background sync

**Schedule**
- Calendar view of upcoming assignments, shift details, route plan

**Materials**
- Material request, usage logging, balance tracking

**Profile**
- Skill classification, certifications, attendance, performance score, training records

---

## 7. Admin Portal (Internal)

### 7.1 Navigation

```
Overview | Owners | Properties | Tenants | Leases | Finance | Operations | Workforce | Vendors | Reports | Configuration
```

**Overview** — platform-wide KPIs: active properties, occupancy, rent collection rate, open tickets, SLA compliance, revenue by package tier.

**Owners / Properties / Tenants / Leases** — full CRUD and record management mirroring owner/tenant app data, with internal-only fields (risk flags, internal notes, approval overrides).

**Finance** — ledger management, invoice verification, expense approval queues, payout processing, financial audit trail.

**Operations** — ticket queue and SLA monitoring, inspection scheduling, preventive maintenance calendar, escalation management.

**Workforce** — technician roster, shift/attendance management, skill and certification tracking, performance dashboards, labour eligibility rule configuration.

**Vendors** — vendor directory, rate cards, performance scoring, work order history, blacklist management.

**Reports** — configurable reports across occupancy, collections, maintenance cost, vendor performance, workforce utilisation, customer satisfaction.

**Configuration** — package/pricing management, SLA rule configuration, notification templates, role-based access control, service category management.

---

## 8. Notification & Communication Matrix

| Trigger | Channel(s) | Recipient |
|---|---|---|
| Rent due / overdue | Push, SMS, Email | Tenant |
| Rent received | Push, Email | Owner |
| Lease expiring soon | Push, Email | Owner, Tenant |
| Document expiring | Push, Email | Owner |
| Maintenance ticket created | Push | Assigned staff/vendor, Owner (if approval needed) |
| Maintenance ticket closed | Push | Tenant, Owner |
| Inspection scheduled | Push, SMS | Tenant, Owner |
| Payment failed | Push, SMS | Tenant |
| Approval required | Push, Email | Owner |
| Emergency alert | Push, SMS, WhatsApp | Owner, Tenant (property-specific) |

---

## 9. Non-Functional & Compliance Requirements

- Role-based access control across all four apps, with property-level and owner-level data isolation.
- Multi-factor authentication for Owner App and Admin Portal.
- End-to-end encryption for KYC and financial data at rest and in transit.
- Full audit logging of approvals, financial transactions, and document access.
- Configurable data retention aligned with applicable data protection regulation.
- Disaster recovery and backup policy for all property and financial records.

---

## 10. Sitemap Summary

```
Public Website
├── Home
├── For Owners
│   ├── Why Mokman
│   ├── List Your Property
│   └── Owner Packages
├── For Tenants
│   ├── Why Mokman
│   ├── Browse Properties (optional)
│   └── Tenant Packages
├── Services
│   ├── Verification & Compliance
│   ├── Rent Collection
│   ├── Property Management
│   ├── Maintenance & Repairs
│   ├── Inspections
│   ├── Insurance
│   ├── Legal & Notices
│   └── Investment Insights
├── Pricing
├── About / Careers / Press / Blog
├── Help Centre / FAQs / Contact
└── Terms / Privacy

Owner App: Dashboard / Properties / Tenants / Finances / Maintenance / Documents / More
Tenant App: Home / Rent / Maintenance / Documents / Messages / Profile
Field Staff App: My Jobs / Schedule / Materials / Profile
Admin Portal: Overview / Owners / Properties / Tenants / Leases / Finance / Operations / Workforce / Vendors / Reports / Configuration
```
