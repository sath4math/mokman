type IconProps = { className?: string; size?: number };

export function IconShieldCheck({ className, size = 24 }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      className={className}
    >
      <path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6l7-3z" strokeLinejoin="round" />
      <path d="M9 12l2 2 4-4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function IconWallet({ className, size = 24 }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      className={className}
    >
      <rect x="3" y="6" width="18" height="13" rx="2" />
      <path d="M3 10h18" />
      <path d="M15 14h3" strokeLinecap="round" />
    </svg>
  );
}

export function IconWrench({ className, size = 24 }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      className={className}
    >
      <path
        d="M14.7 6.3a4 4 0 00-5.4 5.4L4 17l3 3 5.3-5.3a4 4 0 005.4-5.4l-2.3 2.3-2-2 2.3-2.3z"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function IconFileText({ className, size = 24 }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      className={className}
    >
      <path d="M7 3h7l4 4v14H7z" strokeLinejoin="round" />
      <path d="M14 3v4h4" strokeLinejoin="round" />
      <path d="M9 13h6M9 17h6" strokeLinecap="round" />
    </svg>
  );
}

export function IconUsers({ className, size = 24 }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      className={className}
    >
      <circle cx="9" cy="8" r="3" />
      <path d="M2 20c0-3.3 3.1-6 7-6s7 2.7 7 6" strokeLinecap="round" />
      <circle cx="17" cy="8" r="2.5" />
      <path d="M17 12.2c2.8.4 5 2.6 5 5.3" strokeLinecap="round" />
    </svg>
  );
}

export function IconBuilding({ className, size = 24 }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      className={className}
    >
      <rect x="4" y="3" width="10" height="18" />
      <rect x="14" y="9" width="6" height="12" />
      <path d="M7 7h1M10 7h1M7 11h1M10 11h1M7 15h1M10 15h1" strokeLinecap="round" />
    </svg>
  );
}

export function IconClipboardCheck({ className, size = 24 }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      className={className}
    >
      <rect x="5" y="4" width="14" height="17" rx="2" />
      <path d="M9 3h6v3H9z" />
      <path d="M9 13l2 2 4-4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function IconUmbrella({ className, size = 24 }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      className={className}
    >
      <path d="M3 12a9 9 0 0118 0z" strokeLinecap="round" />
      <path d="M12 12v7a2 2 0 01-4 0" strokeLinecap="round" />
      <path d="M12 3v2" strokeLinecap="round" />
    </svg>
  );
}

export function IconScale({ className, size = 24 }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      className={className}
    >
      <path d="M12 3v18M6 21h12" strokeLinecap="round" />
      <path d="M5 7l-3 6a3 3 0 006 0zM19 7l-3 6a3 3 0 006 0z" strokeLinejoin="round" />
      <path d="M3 7h18" strokeLinecap="round" />
    </svg>
  );
}

export function IconArrowRight({ className, size = 16 }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      className={className}
    >
      <path d="M5 12h14M13 6l6 6-6 6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function IconHouse({ className, size = 28 }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      className={className}
    >
      <path d="M4 11.5L12 4l8 7.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M6 10v10h12V10" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M10 20v-6h4v6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
