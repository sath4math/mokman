import { NextResponse, type NextRequest } from "next/server";

import { API_BASE_URL, sessionCookieOptions, SESSION_COOKIE } from "@/lib/session";

export async function POST(request: NextRequest) {
  const body = await request.json();

  const apiResponse = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await apiResponse.json();

  if (!apiResponse.ok) {
    return NextResponse.json(data, { status: apiResponse.status });
  }

  const response = NextResponse.json({ role: data.role });
  response.cookies.set(SESSION_COOKIE, data.access_token, sessionCookieOptions);
  return response;
}
