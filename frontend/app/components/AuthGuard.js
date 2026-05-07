"use client";
import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";

const PUBLIC_PATHS = ["/login"];

export default function AuthGuard({ children }) {
  const router = useRouter();
  const pathname = usePathname();
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (PUBLIC_PATHS.includes(pathname)) {
      // Already on a public page
      setAuthorized(true);
      return;
    }

    if (!token) {
      router.replace("/login");
    } else {
      setAuthorized(true);
    }
  }, [pathname, router]);

  if (PUBLIC_PATHS.includes(pathname)) {
    return children;
  }

  if (!authorized) {
    return null;
  }

  return children;
}
