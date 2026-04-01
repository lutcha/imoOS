/**
 * Email Verification Page — ImoOS
 * Sprint 7 - Prompt 03: Self-Service Onboarding
 * 
 * Handles /verify-email?token={uuid}
 */
"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";

type VerificationStatus =
  | "loading"
  | "verifying"
  | "success"
  | "already_verified"
  | "already_active"
  | "expired"
  | "error";

function VerifyEmailInner() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [status, setStatus] = useState<VerificationStatus>("loading");
  const [message, setMessage] = useState<string>("");
  const [companyName, setCompanyName] = useState<string>("");

  useEffect(() => {
    const token = searchParams.get("token");

    if (!token) {
      setStatus("error");
      setMessage("Token não fornecido. Por favor, verifique o email.");
      return;
    }

    verifyToken(token);
  }, [searchParams]);

  async function verifyToken(token: string) {
    setStatus("verifying");

    try {
      const resp = await fetch(`/api/v1/register/verify/?token=${token}`);
      const data = await resp.json();

      if (resp.ok) {
        if (data.status === "already_verified") {
          setStatus("already_verified");
        } else if (data.status === "already_active") {
          setStatus("already_active");
        } else {
          setStatus("success");
        }
        setMessage(data.message || "Email verificado com sucesso!");
        setCompanyName(data.company_name || "");
      } else {
        setStatus("expired");
        setMessage(data.error || "Token inválido ou expirado.");
      }
    } catch (err) {
      setStatus("error");
      setMessage("Erro de conexão. Por favor, tente novamente.");
    }
  }

  return (
    <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
      {status === "loading" && (
        <>
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">A carregar...</p>
        </>
      )}

      {status === "verifying" && (
        <>
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">A verificar email...</p>
        </>
      )}

      {status === "success" && (
        <>
          <div className="text-6xl mb-4">✅</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Email Verificado!
          </h1>
          <p className="text-gray-600 mb-2">{message}</p>
          {companyName && (
            <p className="text-gray-800 font-medium mb-6">
              {companyName}
            </p>
          )}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-blue-800">
              A sua conta está a ser configurada. Receberá um email com as
              credenciais em breve.
            </p>
          </div>
          <button
            onClick={() => router.push("/login")}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Ir para Login
          </button>
        </>
      )}

      {status === "already_verified" && (
        <>
          <div className="text-6xl mb-4">ℹ️</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Email Já Verificado
          </h1>
          <p className="text-gray-600 mb-2">{message}</p>
          {companyName && (
            <p className="text-gray-800 font-medium mb-6">
              {companyName}
            </p>
          )}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-blue-800">
              A sua conta já está a ser configurada. Receberá um email com as
              credenciais em breve.
            </p>
          </div>
          <button
            onClick={() => router.push("/login")}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Ir para Login
          </button>
        </>
      )}

      {status === "already_active" && (
        <>
          <div className="text-6xl mb-4">🎉</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Conta Activa
          </h1>
          <p className="text-gray-600 mb-2">{message}</p>
          {companyName && (
            <p className="text-gray-800 font-medium mb-6">
              {companyName}
            </p>
          )}
          <button
            onClick={() => router.push("/login")}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Fazer Login
          </button>
        </>
      )}

      {status === "expired" && (
        <>
          <div className="text-6xl mb-4">⏰</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Link Expirado
          </h1>
          <p className="text-gray-600 mb-6">{message}</p>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-yellow-800">
              O link de verificação expirou (48 horas). Por favor, registe-se
              novamente.
            </p>
          </div>
          <button
            onClick={() => router.push("/register")}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Novo Registo
          </button>
        </>
      )}

      {status === "error" && (
        <>
          <div className="text-6xl mb-4">❌</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Erro</h1>
          <p className="text-gray-600 mb-6">{message}</p>
          <button
            onClick={() => router.push("/register")}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Voltar ao Registo
          </button>
        </>
      )}
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Suspense fallback={
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">A carregar...</p>
        </div>
      }>
        <VerifyEmailInner />
      </Suspense>
    </div>
  );
}
