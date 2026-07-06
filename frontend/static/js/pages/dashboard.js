(function () {
  DEMS.requireAuth();
  const user = DEMS.getUser();

  const roleRedirects = { admin: "/admin", counselor: "/counselor", legal: "/legal" };
  if (user && roleRedirects[user.role]) {
    window.location.href = roleRedirects[user.role];
    return;
  }

  renderSupportResources("hotline-container");

  async function loadCases() {
    const listEl = document.getElementById("case-list");
    try {
      const data = await DEMS.request("/api/cases");
      if (!data.cases.length) {
        listEl.innerHTML = '<p class="form-help">You have not filed any cases yet.</p>';
        return;
      }
      listEl.innerHTML = data.cases
        .map((c) => `
          <div class="card">
            ${renderCaseCard(c)}
            <a class="btn secondary" href="/upload-evidence?case_id=${c.id}">Manage evidence</a>
          </div>
        `)
        .join("");
    } catch (err) {
      listEl.innerHTML = `<div class="alert error">${DEMS.escapeHtml(err.message)}</div>`;
    }
  }

  document.getElementById("create-case-btn").addEventListener("click", async () => {
    const alertEl = document.getElementById("create-case-alert");
    const title = document.getElementById("title").value.trim();
    const description = document.getElementById("description").value.trim();
    const is_anonymous = document.getElementById("is_anonymous").checked;

    alertEl.innerHTML = "";
    try {
      await DEMS.request("/api/cases", { method: "POST", body: { title, description, is_anonymous } });
      alertEl.innerHTML = '<div class="alert success">Case submitted. A counselor will be in touch.</div>';
      document.getElementById("title").value = "";
      document.getElementById("description").value = "";
      loadCases();
    } catch (err) {
      alertEl.innerHTML = `<div class="alert error">${DEMS.escapeHtml(err.message)}</div>`;
    }
  });

  loadCases();
})();
