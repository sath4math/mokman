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
