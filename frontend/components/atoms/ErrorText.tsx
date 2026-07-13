export function ErrorText({ children, id }: { children?: string; id?: string }) {
  if (!children) return null;
  return (
    <p id={id} className="mt-1 text-xs font-medium text-danger" role="alert">
      {children}
    </p>
  );
}
