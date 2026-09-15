import { NextResponse, type NextRequest } from "next/server";

import { API_BASE_URL, SESSION_COOKIE } from "@/lib/session";

async function proxy(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> },
): Promise<NextResponse> {
  const { path } = await params;
  const token = request.cookies.get(SESSION_COOKIE)?.value;

  const url = `${API_BASE_URL}/${path.join("/")}${request.nextUrl.search}`;

  const headers: Record<string, string> = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  const contentType = request.headers.get("content-type");
  if (contentType) headers["Content-Type"] = contentType;

  const hasBody = !["GET", "HEAD"].includes(request.method);
  const body = hasBody ? await request.text() : undefined;

  const apiResponse = await fetch(url, { method: request.method, headers, body });

  if (apiResponse.status === 204) {
    return new NextResponse(null, { status: 204 });
  }

  const responseBody = await apiResponse.text();
  return new NextResponse(responseBody, {
    status: apiResponse.status,
    headers: { "Content-Type": apiResponse.headers.get("content-type") ?? "application/json" },
  });
}

export {
  proxy as DELETE,
  proxy as GET,
  proxy as PATCH,
  proxy as POST,
  proxy as PUT,
};
