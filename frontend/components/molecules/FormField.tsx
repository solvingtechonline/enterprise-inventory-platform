import { Label } from "../atoms/Label";
import { ErrorText } from "../atoms/ErrorText";

interface Props {
  htmlFor: string;
  label: string;
  required?: boolean;
  error?: string;
  hint?: string;
  children: React.ReactNode;
}

export function FormField({ htmlFor, label, required, error, hint, children }: Props) {
  return (
    <div>
      <Label htmlFor={htmlFor} required={required}>
        {label}
      </Label>
      <div className="mt-1">{children}</div>
      {hint && !error && <p className="mt-1 text-xs text-ink-muted">{hint}</p>}
      <ErrorText>{error}</ErrorText>
    </div>
  );
}
