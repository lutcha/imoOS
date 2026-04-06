"use client";

/**
 * Service Worker Registration
 * PWA support for ImoOS Field App
 */
import { useEffect } from "react";

export function RegisterSW() {
  useEffect(() => {
    if (typeof window === "undefined") return;
    if (!("serviceWorker" in navigator)) return;

    // Register service worker
    const registerSW = async () => {
      try {
        const registration = await navigator.serviceWorker.register("/sw.js", {
          scope: "/",
        });

        console.log("[PWA] Service Worker registered:", registration);

        // Handle updates
        registration.addEventListener("updatefound", () => {
          const newWorker = registration.installing;
          if (!newWorker) return;

          newWorker.addEventListener("statechange", () => {
            if (newWorker.state === "installed" && navigator.serviceWorker.controller) {
              // New version available
              if (confirm("Nova versão disponível. Atualizar agora?")) {
                newWorker.postMessage({ type: "SKIP_WAITING" });
                window.location.reload();
              }
            }
          });
        });

        // Listen for messages from SW
        navigator.serviceWorker.addEventListener("message", (event) => {
          const { type } = event.data;
          
          if (type === "SYNC_PENDING_TASKS") {
            // Trigger sync from client
            window.dispatchEvent(new CustomEvent("trigger-sync"));
          }
        });

        // Register background sync
        if ("sync" in registration) {
          await registration.sync.register("sync-tasks");
          console.log("[PWA] Background sync registered");
        }

        // Request notification permission
        if ("Notification" in window && Notification.permission === "default") {
          // Don't ask immediately, wait for user interaction
        }

      } catch (error) {
        console.error("[PWA] Service Worker registration failed:", error);
      }
    };

    // Wait for page to load before registering
    if (document.readyState === "complete") {
      registerSW();
    } else {
      window.addEventListener("load", registerSW);
    }

    return () => {
      window.removeEventListener("load", registerSW);
    };
  }, []);

  return null;
}

/**
 * Hook to check PWA install status
 */
export function usePWAStatus() {
  const [canInstall, setCanInstall] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [deferredPrompt, setDeferredPrompt] = useState<Event | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;

    // Check if already installed
    const checkInstalled = () => {
      const isStandalone =
        window.matchMedia("(display-mode: standalone)").matches ||
        (window.navigator as unknown as { standalone?: boolean }).standalone === true;
      setIsInstalled(isStandalone);
    };

    checkInstalled();

    // Listen for beforeinstallprompt
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setCanInstall(true);
    };

    // Listen for appinstalled
    const handleAppInstalled = () => {
      setCanInstall(false);
      setIsInstalled(true);
      setDeferredPrompt(null);
      console.log("[PWA] App installed");
    };

    window.addEventListener("beforeinstallprompt", handleBeforeInstallPrompt);
    window.addEventListener("appinstalled", handleAppInstalled);

    return () => {
      window.removeEventListener("beforeinstallprompt", handleBeforeInstallPrompt);
      window.removeEventListener("appinstalled", handleAppInstalled);
    };
  }, []);

  const install = async () => {
    if (!deferredPrompt) return;

    const promptEvent = deferredPrompt as {
      prompt: () => void;
      userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
    };

    promptEvent.prompt();

    const { outcome } = await promptEvent.userChoice;
    if (outcome === "accepted") {
      setDeferredPrompt(null);
      setCanInstall(false);
    }
  };

  return { canInstall, isInstalled, install };
}

// Import useState for the hook
import { useState } from "react";
