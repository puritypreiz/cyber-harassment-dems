(function () {
  const alertEl = document.getElementById("login-alert");
  const mfaField = document.getElementById("mfa-field");

  async function doLogin() {
    const username_or_email = document.getElementById("username_or_email").value.trim();
    const password = document.getElementById("password").value;
    const totp_code = document.getElementById("totp_code").value.trim();

    alertEl.innerHTML = "";
    try {
      const data = await DEMS.request("/api/auth/login", {
        method: "POST",
        body: { username_or_email, password, totp_code: totp_code || undefined },
      });
      DEMS.setSession(data.user, data.access_token, data.refresh_token);
      window.location.href = "/dashboard";
    } catch (err) {
      if (err.message === "mfa_code_required") {
        mfaField.classList.remove("hidden");
        alertEl.innerHTML = '<div class="alert info">Enter your multi-factor authentication code to continue.</div>';
      } else {
        alertEl.innerHTML = `<div class="alert error">${DEMS.escapeHtml(err.message)}</div>`;
      }
    }
  }

  document.getElementById("login-btn").addEventListener("click", doLogin);
})();
