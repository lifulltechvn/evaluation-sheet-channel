/**
 * Decode JWT payload without external library.
 * Returns the decoded payload object or null if invalid.
 */
export function decodeToken(token) {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;

    const payload = parts[1];
    // Handle base64url encoding
    const base64 = payload.replace(/-/g, "+").replace(/_/g, "/");
    const json = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );
    return JSON.parse(json);
  } catch {
    return null;
  }
}

/**
 * Check if a JWT token is expired.
 * Returns true if expired or invalid.
 */
export function isTokenExpired(token) {
  const payload = decodeToken(token);
  if (!payload || !payload.exp) return true;

  // exp is in seconds, Date.now() is in milliseconds
  const now = Math.floor(Date.now() / 1000);
  return payload.exp < now;
}

/**
 * Get the current valid token, or null if missing/expired.
 * If expired, clears localStorage.
 */
export function getValidToken() {
  const token = localStorage.getItem("access_token");
  if (!token) return null;

  if (isTokenExpired(token)) {
    clearAuth();
    return null;
  }

  return token;
}

/**
 * Get user info from the stored token payload.
 */
export function getUserFromToken() {
  const token = localStorage.getItem("access_token");
  if (!token) return null;

  const payload = decodeToken(token);
  if (!payload) return null;

  return {
    id: payload.sub,
    email: payload.email,
    role: payload.role,
    permissions: payload.permissions || {},
  };
}

/**
 * Clear all auth data from localStorage.
 */
export function clearAuth() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("user");
}
