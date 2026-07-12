export function ErrorText({ children, id }: { children?: string; id?: string }) {
  if (!children) return null;
  return (
    <p id={id} className="mt-1 text-xs text-danger" role="alert">
      {children}
    </p>
  );
}
