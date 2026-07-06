const DEMS = (() => {
  const ACCESS_KEY = "dems_access_token";
  const REFRESH_KEY = "dems_refresh_token";
  const USER_KEY = "dems_user";

  function getAccessToken() { return sessionStorage.getItem(ACCESS_KEY); }
  function getRefreshToken() { return sessionStorage.getItem(REFRESH_KEY); }
  function getUser() {
    const raw = sessionStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  }

  function setSession(user, accessToken, refreshToken) {
    sessionStorage.setItem(USER_KEY, JSON.stringify(user));
    sessionStorage.setItem(ACCESS_KEY, accessToken);
    if (refreshToken) sessionStorage.setItem(REFRESH_KEY, refreshToken);
  }

  function setAccessToken(token) { sessionStorage.setItem(ACCESS_KEY, token); }

  function clearSession() {
    sessionStorage.removeItem(ACCESS_KEY);
    sessionStorage.removeItem(REFRESH_KEY);
    sessionStorage.removeItem(USER_KEY);
  }

  async function refreshAccessToken() {
    const refreshToken = getRefreshToken();
    if (!refreshToken) throw new Error("No refresh token available.");
    const res = await fetch("/api/auth/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!res.ok) throw new Error("Session expired. Please log in again.");
    const data = await res.json();
    setAccessToken(data.access_token);
    return data.access_token;
  }

  async function request(path, options = {}) {
    const opts = { ...options };
    opts.headers = { ...(opts.headers || {}) };

    if (!(opts.body instanceof FormData) && opts.body && typeof opts.body !== "string") {
      opts.body = JSON.stringify(opts.body);
      opts.headers["Content-Type"] = "application/json";
    }

    const accessToken = getAccessToken();
    if (accessToken) opts.headers["Authorization"] = `Bearer ${accessToken}`;

    let res = await fetch(path, opts);

    if (res.status === 401 && getRefreshToken()) {
      try {
        const newToken = await refreshAccessToken();
        opts.headers["Authorization"] = `Bearer ${newToken}`;
        res = await fetch(path, opts);
      } catch (_err) {
        clearSession();
        window.location.href = "/login";
        throw new Error("Session expired.");
      }
    }

    let data = null;
    try { data = await res.json(); } catch (_err) { /* not JSON, e.g. file download */ }

    if (!res.ok) {
      const message = (data && (data.error || JSON.stringify(data.errors))) || `Request failed (${res.status}).`;
      throw new Error(message);
    }
    return data;
  }

  function requireAuth() {
    if (!getAccessToken()) {
      window.location.href = "/login";
    }
  }

  function requireRole(...roles) {
    const user = getUser();
    if (!user || !roles.includes(user.role)) {
      window.location.href = "/dashboard";
    }
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str == null ? "" : String(str);
    return div.innerHTML;
  }

  return {
    request, getUser, setSession, clearSession, requireAuth, requireRole, escapeHtml, getAccessToken,
  };
})();
