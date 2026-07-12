"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "../atoms/Button";
import { Input } from "../atoms/Input";
import { FormField } from "../molecules/FormField";
import { Alert } from "../molecules/Alert";
import { useAuth } from "../../lib/auth/AuthContext";
import { ApiError } from "../../lib/api/http";

function validarCorreo(correo: string): string | undefined {
  if (!correo.trim()) return "El correo es obligatorio.";
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo)) return "Ingresa un correo válido.";
  return undefined;
}

function validarPassword(password: string): string | undefined {
  if (!password) return "La contraseña es obligatoria.";
  return undefined;
}

export function LoginForm() {
  const { login } = useAuth();
  const router = useRouter();

  const [correo, setCorreo] = useState("");
  const [password, setPassword] = useState("");
  const [mostrarPassword, setMostrarPassword] = useState(false);
  const [errores, setErrores] = useState<{ correo?: string; password?: string }>({});
  const [errorGeneral, setErrorGeneral] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setErrorGeneral(null);

    const erroresCampos = {
      correo: validarCorreo(correo),
      password: validarPassword(password),
    };
    setErrores(erroresCampos);
    if (erroresCampos.correo || erroresCampos.password) return;

    setIsLoading(true);
    try {
      await login(correo.trim(), password);
      router.push("/");
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        setErrorGeneral("Correo o contraseña incorrectos.");
      } else if (error instanceof ApiError) {
        setErrorGeneral(error.message);
      } else {
        setErrorGeneral("Ocurrió un error inesperado. Intenta de nuevo.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} noValidate className="space-y-4">
      {errorGeneral && <Alert tono="peligro">{errorGeneral}</Alert>}

      <FormField htmlFor="correo" label="Correo electrónico" required error={errores.correo}>
        <Input
          id="correo"
          type="email"
          autoComplete="username"
          value={correo}
          onChange={(event) => setCorreo(event.target.value)}
          invalid={Boolean(errores.correo)}
          placeholder="admin@empresa.com"
        />
      </FormField>

      <FormField htmlFor="password" label="Contraseña" required error={errores.password}>
        <div className="relative">
          <Input
            id="password"
            type={mostrarPassword ? "text" : "password"}
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            invalid={Boolean(errores.password)}
            placeholder="••••••••"
            className="pr-10"
          />
          <button
            type="button"
            onClick={() => setMostrarPassword((valor) => !valor)}
            aria-label={mostrarPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
            className="absolute inset-y-0 right-0 flex items-center px-3 text-ink-muted
              hover:text-ink focus-visible:outline focus-visible:outline-2
              focus-visible:outline-offset-2 focus-visible:outline-primary"
          >
            {mostrarPassword ? (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.75"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-4 w-4"
                aria-hidden="true"
              >
                <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" />
                <circle cx="12" cy="12" r="3" />
                <line x1="3" y1="21" x2="21" y2="3" />
              </svg>
            ) : (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.75"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-4 w-4"
                aria-hidden="true"
              >
                <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
            )}
          </button>
        </div>
      </FormField>

      <Button type="submit" className="w-full" isLoading={isLoading}>
        Iniciar sesión
      </Button>

      <p className="text-center text-xs text-ink-muted">
        ¿Solo quieres consultar Empresas? No necesitas cuenta:{" "}
        <a href="/empresas" className="text-primary underline underline-offset-2">
          entra como visitante
        </a>
        .
      </p>
    </form>
  );
}
