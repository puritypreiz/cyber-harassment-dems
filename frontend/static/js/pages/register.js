(function () {
  const alertEl = document.getElementById("register-alert");

  document.getElementById("register-btn").addEventListener("click", async () => {
    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    alertEl.innerHTML = "";
    try {
      await DEMS.request("/api/auth/register", { method: "POST", body: { username, email, password } });
      alertEl.innerHTML = '<div class="alert success">Account created. You can now log in.</div>';
      setTimeout(() => { window.location.href = "/login"; }, 1000);
    } catch (err) {
      alertEl.innerHTML = `<div class="alert error">${DEMS.escapeHtml(err.message)}</div>`;
    }
  });
})();
