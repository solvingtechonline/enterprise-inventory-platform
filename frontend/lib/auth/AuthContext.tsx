"use client";

/**
 * Estado de sesión global.
 *
 * Solo el Administrador se autentica; mientras no haya sesión, el
 * estado por defecto es "externo" (visitante de solo lectura), sin
 * necesidad de ningún flujo de login.
 */

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { login as loginRequest } from "../api/auth";
import { ApiError } from "../api/http";
import type { Rol } from "../types/auth";
import { decodeTokenPayload, tokenEstaVencido } from "./decodeToken";

const STORAGE_KEY = "lite-thinking:sesion";

interface SesionAlmacenada {
  access: string;
  refresh: string;
}

interface AuthContextValue {
  token: string | null;
  rol: Rol;
  correo: string | null;
  isAdmin: boolean;
  isReady: boolean;
  login: (correo: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function leerSesionGuardada(): SesionAlmacenada | null {
  if (typeof window === "undefined") return null;
  const crudo = window.localStorage.getItem(STORAGE_KEY);
  if (!crudo) return null;
  try {
    return JSON.parse(crudo) as SesionAlmacenada;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [correo, setCorreo] = useState<string | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // Sincroniza el estado de sesión con localStorage al montar (una API
    // externa al render de React; no puede leerse durante SSR ni durante
    // el render mismo).
    /* eslint-disable react-hooks/set-state-in-effect */
    const sesion = leerSesionGuardada();
    if (!sesion) {
      setIsReady(true);
      return;
    }
    const payload = decodeTokenPayload(sesion.access);
    if (!payload || tokenEstaVencido(payload)) {
      window.localStorage.removeItem(STORAGE_KEY);
      setIsReady(true);
      return;
    }
    setToken(sesion.access);
    setCorreo(payload.correo);
    setIsReady(true);
    /* eslint-enable react-hooks/set-state-in-effect */
  }, []);

  const login = useCallback(async (correoInput: string, password: string) => {
    const respuesta = await loginRequest(correoInput, password);
    const payload = decodeTokenPayload(respuesta.access);
    if (!payload || payload.rol !== "administrador") {
      throw new ApiError("El token recibido no tiene un rol válido.", 500);
    }
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ access: respuesta.access, refresh: respuesta.refresh }),
    );
    setToken(respuesta.access);
    setCorreo(payload.correo);
  }, []);

  const logout = useCallback(() => {
    window.localStorage.removeItem(STORAGE_KEY);
    setToken(null);
    setCorreo(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      correo,
      rol: token ? "administrador" : "externo",
      isAdmin: Boolean(token),
      isReady,
      login,
      logout,
    }),
    [token, correo, isReady, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth debe usarse dentro de un <AuthProvider>.");
  }
  return context;
}
