import type { Metadata } from "next";
import { Inter, Sora } from "next/font/google";
import "./globals.css";

import { Navbar } from "../components/organisms/Navbar";
import { Footer } from "../components/organisms/Footer";
import { AuthProvider } from "../lib/auth/AuthContext";

const sora = Sora({
  subsets: ["latin"],
  weight: ["600", "700"],
  variable: "--font-sora",
  display: "swap",
});

const inter = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Lite Thinking 2026",
  description: "Gestión de Empresas, Productos e Inventario",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className={`h-full antialiased ${sora.variable} ${inter.variable}`}>
      <body className="min-h-full flex flex-col font-sans">
        <AuthProvider>
          <Navbar />
          {children}
          <Footer />
        </AuthProvider>
      </body>
    </html>
  );
}
