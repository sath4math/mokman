export type OwnershipType = "single" | "joint";
export type KycStatus = "pending" | "verified" | "rejected";
export type PropertyStatus = "vacant" | "occupied" | "under_maintenance" | "inactive";
export type OwnerPackage = "starter" | "managed" | "full_care" | "complete";

export interface OwnerProfile {
  pan_number: string | null;
  id_proof_type: string | null;
  id_proof_number: string | null;
  bank_account_number: string | null;
  bank_ifsc: string | null;
  bank_name: string | null;
  ownership_type: OwnershipType;
  ownership_percentage: number | null;
  nominee_name: string | null;
  nominee_relationship: string | null;
  nominee_phone: string | null;
  emergency_contact_name: string | null;
  emergency_contact_phone: string | null;
  kyc_status: KycStatus;
  package: OwnerPackage;
}

export interface AuthorizedRepresentative {
  id: string;
  name: string;
  relationship: string | null;
  phone: string | null;
  email: string | null;
}

export interface Property {
  id: string;
  owner_id: string;
  category: string;
  name: string;
  address_line: string;
  city: string;
  state: string;
  postal_code: string;
  latitude: number | null;
  longitude: number | null;
  status: PropertyStatus;
  area_sqft: number | null;
  num_floors: number | null;
  num_units: number | null;
  amenities: string[] | null;
  furnishing_status: string | null;
  purchase_price: number | null;
  current_market_value: number | null;
}

export interface InvestmentSummary {
  property_id: string;
  property_name: string;
  purchase_price: number | null;
  current_market_value: number | null;
  appreciation_percentage: number | null;
  trailing_12_month_rent_income: number;
  gross_yield_percentage: number | null;
  total_net_income_all_time: number;
  roi_percentage: number | null;
}

export interface PropertyHealthScore {
  score: number;
  open_tickets: number;
  repeat_failure_tickets: number;
  sla_breached_tickets: number;
  overdue_pm_items: number;
  overdue_inspection_followups: number;
}

export interface SaleReadiness {
  property_id: string;
  is_ready: boolean;
  open_tickets: number;
  has_active_lease: boolean;
  unsettled_insurance_claims: number;
  incomplete_renovation_projects: number;
}

export type SaleStatus = "listed" | "under_negotiation" | "agreement_signed" | "completed" | "cancelled";

export interface PropertySale {
  id: string;
  property_id: string;
  status: SaleStatus;
  listing_price: number | null;
  sale_price: number | null;
  buyer_name: string | null;
  buyer_contact: string | null;
  agreement_date: string | null;
  settlement_date: string | null;
  ownership_transferred: boolean;
  utilities_transferred: boolean;
  society_transferred: boolean;
  notes: string | null;
}

export interface DocumentRecord {
  id: string;
  owner_type: string;
  owner_id: string;
  document_type: string;
  version: number;
  expiry_date: string | null;
  ocr_status: string;
}

export type TenantVerificationStatus = "pending" | "verified" | "rejected";

export interface TenantProfile {
  id_proof_type: string | null;
  id_proof_number: string | null;
  occupants_count: number | null;
  vehicles: string[] | null;
  pets: string[] | null;
  emergency_contact_name: string | null;
  emergency_contact_phone: string | null;
  verification_status: TenantVerificationStatus;
}

export type LeaseStatus = "draft" | "pending_acknowledgment" | "active" | "terminated" | "expired";

export interface Lease {
  id: string;
  property_id: string;
  tenant_id: string;
  start_date: string;
  end_date: string;
  monthly_rent: number;
  security_deposit: number;
  lock_in_period_months: number | null;
  notice_period_days: number | null;
  annual_escalation_percentage: number | null;
  responsibilities: string | null;
  status: LeaseStatus;
  owner_acknowledged_at: string | null;
  tenant_acknowledged_at: string | null;
  previous_lease_id: string | null;
}

export type InspectionType = "move_in" | "move_out" | "scheduled" | "ticket_triggered";

export interface Inspection {
  id: string;
  property_id: string;
  lease_id: string | null;
  inspection_type: InspectionType;
  conducted_by: string;
  checklist: Record<string, string> | null;
  notes: string | null;
  meter_readings: Record<string, string> | null;
  owner_signed_off_at: string | null;
  tenant_signed_off_at: string | null;
  deposit_deduction: number | null;
  deposit_refund: number | null;
  settled_at: string | null;
  scheduled_for: string | null;
  triggered_by_ticket_id: string | null;
  follow_up_notes: string | null;
  follow_up_due_on: string | null;
}

export type InvoiceStatus = "pending" | "partially_paid" | "paid" | "overdue" | "cancelled";

export interface RentInvoice {
  id: string;
  lease_id: string;
  property_id: string;
  period_start: string;
  period_end: string;
  due_date: string;
  amount_due: number;
  status: InvoiceStatus;
}

export interface RentEscalationProjection {
  lease_id: string;
  property_id: string;
  current_rent: number;
  projected_rent: number;
  escalation_date: string;
}

export type LedgerEntryType =
  | "rent_payment"
  | "mokman_fee"
  | "deposit_collected"
  | "deposit_deduction"
  | "deposit_refund"
  | "expense";

export interface LedgerEntry {
  id: string;
  property_id: string;
  lease_id: string | null;
  invoice_id: string | null;
  expense_id: string | null;
  inspection_id: string | null;
  entry_type: LedgerEntryType;
  amount: number;
  method: string | null;
  reference_note: string | null;
  recorded_by: string;
  occurred_at: string;
}

export interface PropertyStatement {
  year: number;
  month: number;
  rent_collected: number;
  expenses: number;
  mokman_fee: number;
  net_payable: number;
  entries: LedgerEntry[];
}

export interface PropertyProfitability {
  property_id: string;
  property_name: string;
  year: number;
  month: number;
  net_payable: number;
}

export interface ExpenseAnomaly {
  expense_id: string;
  property_id: string;
  category: string;
  amount: number;
  reason: string;
}

export type ExpenseStatus = "pending" | "approved" | "rejected";

export interface Expense {
  id: string;
  property_id: string;
  category: string;
  amount: number;
  description: string | null;
  status: ExpenseStatus;
  submitted_by: string;
  approved_by: string | null;
  approved_at: string | null;
  vendor_id: string | null;
  ticket_id: string | null;
}

export type TicketStatus =
  | "open"
  | "diagnosed"
  | "estimated"
  | "approved"
  | "assigned"
  | "in_progress"
  | "resolved"
  | "closed";
export type TicketPriority = "low" | "medium" | "high" | "urgent";

export interface MaintenanceTicket {
  id: string;
  property_id: string;
  category: string;
  description: string;
  priority: TicketPriority;
  status: TicketStatus;
  raised_by: string;
  assigned_to: string | null;
  assigned_vendor_id: string | null;
  resolution_notes: string | null;
  closed_at: string | null;
  created_at: string;
  sla_due_at: string | null;
  sla_breached_at: string | null;
  diagnosis_notes: string | null;
  diagnosed_at: string | null;
  diagnosed_by: string | null;
  estimated_cost: number | null;
  estimated_at: string | null;
  estimated_by: string | null;
  approved_at: string | null;
  approved_by: string | null;
  checklist: Record<string, boolean> | null;
  check_in_at: string | null;
  check_in_latitude: number | null;
  check_in_longitude: number | null;
  check_out_at: string | null;
  check_out_latitude: number | null;
  check_out_longitude: number | null;
  rework_count: number;
  warranty_expires_on: string | null;
  is_repeat_failure: boolean;
  related_ticket_id: string | null;
  eligibility_outcome: EligibilityOutcome | null;
  fair_use_breached: boolean;
  asset_id: string | null;
}

export interface ChecklistTemplate {
  id: string;
  category: string;
  items: string[];
  is_active: boolean;
}

export interface ServiceCategory {
  id: string;
  name: string;
  default_priority: TicketPriority;
  estimated_completion_hours: number | null;
  is_active: boolean;
}

export type EligibilityOutcome = "included" | "chargeable" | "third_party" | "out_of_scope" | "escalate";

export interface ServiceEligibilityRule {
  id: string;
  service_category_id: string;
  package: OwnerPackage;
  outcome: EligibilityOutcome;
  notes: string | null;
  max_occurrences: number | null;
  period_days: number | null;
  max_value: number | null;
}

export interface MaterialUsage {
  id: string;
  ticket_id: string;
  item: string;
  quantity: number;
  unit_cost: number;
  is_wastage: boolean;
  logged_by: string;
  expense_id: string | null;
  created_at: string;
}

export interface RecurringProblem {
  property_id: string;
  property_name: string;
  category: string;
  ticket_count: number;
  window_days: number;
}

export interface FieldStaffUser {
  id: string;
  full_name: string | null;
  email: string | null;
}

export interface Vendor {
  id: string;
  name: string;
  service_category: string;
  phone: string | null;
  email: string | null;
  gst_number: string | null;
  pan_number: string | null;
  notes: string | null;
  is_active: boolean;
  average_rating: number | null;
}

export interface VendorHistoryEvent {
  id: string;
  actor_id: string | null;
  action: string;
  after: Record<string, unknown> | null;
  created_at: string;
}

export interface VendorRateCard {
  id: string;
  vendor_id: string;
  service_category: string;
  unit: string;
  rate: number;
  notes: string | null;
}

export interface VendorRating {
  id: string;
  vendor_id: string;
  ticket_id: string;
  rated_by: string;
  score: number;
  notes: string | null;
  created_at: string;
}

export interface MaintenanceSchedule {
  id: string;
  property_id: string;
  category: string;
  frequency_days: number;
  last_serviced_on: string | null;
  next_due_on: string;
  warranty_expires_on: string | null;
  notes: string | null;
  is_active: boolean;
  asset_id: string | null;
}

export interface Asset {
  id: string;
  property_id: string;
  category: string;
  name: string;
  purchase_date: string | null;
  purchase_cost: number | null;
  vendor_id: string | null;
  warranty_expires_on: string | null;
  useful_life_years: number | null;
  is_active: boolean;
  disposed_reason: string | null;
  replaced_by_asset_id: string | null;
  current_value: number | null;
}

export type ClaimStatus = "filed" | "under_review" | "approved" | "rejected" | "settled";

export interface InsurancePolicy {
  id: string;
  property_id: string;
  policy_number: string;
  insurer_name: string;
  category: string;
  premium_amount: number;
  premium_due_date: string | null;
  coverage_amount: number | null;
  start_date: string;
  end_date: string;
  is_active: boolean;
}

export interface InsuranceClaim {
  id: string;
  policy_id: string;
  incident_date: string;
  description: string;
  claim_amount: number;
  status: ClaimStatus;
  surveyor_name: string | null;
  settlement_amount: number | null;
  settled_at: string | null;
}

export type ProjectStatus = "requested" | "approved" | "in_progress" | "completed" | "cancelled";

export interface RenovationProject {
  id: string;
  property_id: string;
  title: string;
  description: string | null;
  vendor_id: string | null;
  status: ProjectStatus;
  budget_amount: number | null;
  start_date: string | null;
  end_date: string | null;
  completed_at: string | null;
  warranty_expires_on: string | null;
}

export interface ProjectMilestone {
  id: string;
  project_id: string;
  title: string;
  due_date: string | null;
  payment_amount: number;
  completed_at: string | null;
  paid_at: string | null;
  expense_id: string | null;
}

export type UtilityResponsibility = "owner" | "tenant";

export interface UtilityConnection {
  id: string;
  property_id: string;
  utility_type: string;
  provider: string | null;
  account_number: string | null;
  responsibility: UtilityResponsibility;
  is_active: boolean;
}

export interface UtilityBill {
  id: string;
  connection_id: string;
  billing_period_start: string;
  billing_period_end: string;
  amount: number;
  due_date: string;
  meter_reading: number | null;
  paid_at: string | null;
  paid_by: string | null;
}

export type ComplianceCategory = "society_maintenance" | "property_tax" | "other";

export interface ComplianceDue {
  id: string;
  property_id: string;
  category: ComplianceCategory;
  description: string | null;
  amount: number;
  due_date: string;
  paid_at: string | null;
  paid_reference: string | null;
}
