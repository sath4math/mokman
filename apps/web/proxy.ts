import { jwtVerify } from "jose";
import { NextResponse, type NextRequest } from "next/server";

import { ROLE_HOME, SESSION_COOKIE } from "@/lib/session";

const PROTECTED_ROLE_BY_PREFIX: Record<string, string> = {
  "/owner": "owner",
  "/tenant": "tenant",
  "/field": "field_staff",
  "/admin": "admin",
};

async function getRoleFromToken(token: string | undefined): Promise<string | null> {
  if (!token || !process.env.JWT_SECRET) return null;
  try {
    const secret = new TextEncoder().encode(process.env.JWT_SECRET);
    const { payload } = await jwtVerify(token, secret);
    return typeof payload.role === "string" ? payload.role : null;
  } catch {
    return null;
  }
}

export async function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const matchedPrefix = Object.keys(PROTECTED_ROLE_BY_PREFIX).find((prefix) =>
    pathname.startsWith(prefix),
  );
  if (!matchedPrefix) return NextResponse.next();

  const token = request.cookies.get(SESSION_COOKIE)?.value;
  const role = await getRoleFromToken(token);

  if (!role) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  const requiredRole = PROTECTED_ROLE_BY_PREFIX[matchedPrefix];
  if (role !== requiredRole) {
    return NextResponse.redirect(new URL(ROLE_HOME[role] ?? "/", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/owner/:path*", "/tenant/:path*", "/field/:path*", "/admin/:path*"],
};
