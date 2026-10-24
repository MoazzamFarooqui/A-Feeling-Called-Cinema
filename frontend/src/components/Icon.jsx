const ICONS = {
  home: (
    <>
      <path d="M3 10.5 12 3l9 7.5" />
      <path d="M5 9.5V21h5v-6h4v6h5V9.5" />
    </>
  ),
  sparkles: (
    <>
      <path d="m12 2.5 2 5.5 5.5 2-5.5 2-2 5.5-2-5.5L4.5 10 10 8z" />
      <path d="m19 15 .9 2.1L22 18l-2.1.9L19 21l-.9-2.1L16 18l2.1-.9z" />
    </>
  ),
  users: (
    <>
      <circle cx="9" cy="8" r="3.2" />
      <path d="M2.8 20.4v-1.6a4.6 4.6 0 0 1 4.6-4.6h3.2a4.6 4.6 0 0 1 4.6 4.6v1.6" />
      <path d="M16.2 4.9a3.2 3.2 0 0 1 0 6.2" />
      <path d="M18 14.4a4.6 4.6 0 0 1 3.2 4.4v1.6" />
    </>
  ),
  clock: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5.2l3.4 2" />
    </>
  ),
  layers: (
    <>
      <path d="M12 2.5 2.5 7.5 12 12.5l9.5-5z" />
      <path d="m2.5 12.5 9.5 5 9.5-5" />
      <path d="m2.5 17 9.5 5 9.5-5" />
    </>
  ),
  globe: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M3 12h18" />
      <path d="M12 3c3.2 2.4 5 5.7 5 9s-1.8 6.6-5 9c-3.2-2.4-5-5.7-5-9s1.8-6.6 5-9z" />
    </>
  ),
  hourglass: (
    <>
      <path d="M6 2.5h12" />
      <path d="M6 21.5h12" />
      <path d="M7 2.5c0 5 4 6.2 5 9.5-1 3.3-5 4.5-5 9.5" />
      <path d="M17 2.5c0 5-4 6.2-5 9.5 1 3.3 5 4.5 5 9.5" />
    </>
  ),
  gem: (
    <>
      <path d="M7 3.5h10l4 5.5-9 12-9-12z" />
      <path d="M3 9h18" />
      <path d="M9.5 3.5 12 9l2.5-5.5" />
      <path d="m9 9 3 12" />
      <path d="m15 9-3 12" />
    </>
  ),
  star: (
    <path
      fill="currentColor"
      stroke="none"
      d="m12 3.2 2.7 5.6 6.1.8-4.5 4.3 1.1 6-5.4-3-5.4 3 1.1-6-4.5-4.3 6.1-.8z"
    />
  ),
  target: (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <circle cx="12" cy="12" r="4.5" />
      <circle cx="12" cy="12" r="1" fill="currentColor" stroke="none" />
    </>
  ),
  search: (
    <>
      <circle cx="11" cy="11" r="7" />
      <path d="M20.5 20.5 16.2 16.2" />
    </>
  ),
  arrow: (
    <>
      <path d="M5 12h14" />
      <path d="m13 6 6 6-6 6" />
    </>
  ),
  film: (
    <>
      <rect x="3" y="3" width="18" height="18" rx="4" />
      <path d="M7 3v18M17 3v18M3 8h4M17 8h4M3 16h4M17 16h4" />
    </>
  ),
  close: (
    <>
      <path d="m6 6 12 12" />
      <path d="M18 6 6 18" />
    </>
  ),
  plus: (
    <>
      <path d="M12 5v14" />
      <path d="M5 12h14" />
    </>
  ),
}

export default function Icon({ name, size = 20, strokeWidth = 1.7, className = '' }) {
  return (
    <svg
      className={className}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
    >
      {ICONS[name] || ICONS.sparkles}
    </svg>
  )
}
