import { LoginForm } from "../../components/organisms/LoginForm";

export default function LoginPage() {
  return (
    <div className="flex flex-1 items-center justify-center px-6 py-16">
      <div className="w-full max-w-sm rounded-md border border-border bg-surface p-8 shadow-sm">
        <div className="mb-6 text-center">
          <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">
            Lite Thinking · libro mayor
          </p>
          <h1 className="mt-1 font-display text-xl text-ink">Acceso de Administrador</h1>
        </div>
        <LoginForm />
      </div>
    </div>
  );
}
