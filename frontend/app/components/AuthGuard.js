"use client";
import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { getValidToken, clearAuth } from "../utils/auth";

const PUBLIC_PATHS = ["/login"];

export default function AuthGuard({ children }) {
  const router = useRouter();
  const pathname = usePathname();
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    if (PUBLIC_PATHS.includes(pathname)) {
      setAuthorized(true);
      return;
    }

    const token = getValidToken();

    if (!token) {
      // Token missing or expired — clear and redirect
      clearAuth();
      router.replace("/login");
      setAuthorized(false);
    } else {
      setAuthorized(true);
    }
  }, [pathname, router]);

  // Periodically check token expiration (every 60s)
  useEffect(() => {
    if (PUBLIC_PATHS.includes(pathname)) return;

    const interval = setInterval(() => {
      const token = getValidToken();
      if (!token) {
        clearAuth();
        router.replace("/login");
        setAuthorized(false);
      }
    }, 60000);

    return () => clearInterval(interval);
  }, [pathname, router]);

  if (PUBLIC_PATHS.includes(pathname)) {
    return children;
  }

  if (!authorized) {
    return null;
  }

  return children;
}
