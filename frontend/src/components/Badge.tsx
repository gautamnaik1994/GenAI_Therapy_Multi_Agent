function Badge({
  children,
  variant,
}: {
  children: React.ReactNode;
  variant: string;
}) {
  return <span className={`badge bg-${variant}`}>{children}</span>;
}
export default Badge;
