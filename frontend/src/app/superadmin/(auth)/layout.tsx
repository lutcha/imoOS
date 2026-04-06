/**
 * Superadmin auth layout — no auth guard, just renders children.
 * Used for /superadmin/login which must be accessible without a session.
 */
export default function SuperAdminAuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
