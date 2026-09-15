export const SESSION_COOKIE = "mokman_token";

export const sessionCookieOptions = {
  httpOnly: true,
  secure: process.env.NODE_ENV === "production",
  sameSite: "lax" as const,
  path: "/",
  maxAge: 60 * 60 * 24, // 1 day — matches JWT_ACCESS_TOKEN_EXPIRE_MINUTES default
};

export const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000";

export const ROLE_HOME: Record<string, string> = {
  owner: "/owner",
  tenant: "/tenant",
  field_staff: "/field",
  admin: "/admin",
};

export interface CurrentUser {
  id: string;
  email: string | null;
  full_name: string | null;
  role: string;
}
