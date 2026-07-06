(function () {
  DEMS.requireAuth();
  DEMS.requireRole("legal");

  async function loadCases() {
    const el = document.getElementById("case-list");
    try {
      const data = await DEMS.request("/api/cases");
      el.innerHTML = data.cases.length
        ? data.cases.map((c) => `
            <div class="card">
              ${renderCaseCard(c)}
              <a class="btn secondary" href="/reports?case_id=${c.id}">Export chain-of-custody report</a>
            </div>
          `).join("")
        : '<p class="form-help">No cases currently assigned to you.</p>';
    } catch (err) {
      el.innerHTML = `<div class="alert error">${DEMS.escapeHtml(err.message)}</div>`;
    }
  }

  loadCases();
})();
