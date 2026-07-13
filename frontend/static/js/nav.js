(function () {
  const user = DEMS.getUser();
  const logoutLink = document.getElementById("nav-logout");
  const loginLink = document.getElementById("nav-login");
  const registerLink = document.getElementById("nav-register");
  if (user) {
    loginLink.classList.add("hidden");
    registerLink.classList.add("hidden");
    logoutLink.classList.remove("hidden");
    logoutLink.addEventListener("click", async (e) => {
      e.preventDefault();
      try { await DEMS.request("/api/auth/logout", { method: "POST" }); } catch (_err) {}
      DEMS.clearSession();
      window.location.href = "/";
    });
  }
})();