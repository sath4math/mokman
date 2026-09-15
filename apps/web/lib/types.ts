export type OwnershipType = "single" | "joint";
export type KycStatus = "pending" | "verified" | "rejected";
export type PropertyStatus = "vacant" | "occupied" | "under_maintenance" | "inactive";

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

export type InspectionType = "move_in" | "move_out";

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
}
