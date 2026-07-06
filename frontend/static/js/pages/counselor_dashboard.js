(function () {
  DEMS.requireAuth();
  DEMS.requireRole("counselor");

  async function loadCases() {
    const el = document.getElementById("case-list");
    try {
      const data = await DEMS.request("/api/cases");
      el.innerHTML = data.cases.length
        ? data.cases.map((c) => `
            <div class="card">
              ${renderCaseCard(c)}
              <label for="status-${c.id}">Update status</label>
              <select id="status-${c.id}">
                ${["open", "under_review", "escalated", "resolved", "closed"].map((s) => `<option value="${s}" ${s === c.status ? "selected" : ""}>${s}</option>`).join("")}
              </select>
              <button class="btn" data-case-id="${c.id}" data-action="update-status" style="margin-top:0.5rem;">Save status</button>
              <div id="status-result-${c.id}" style="margin-top:0.5rem;"></div>
            </div>
          `).join("")
        : '<p class="form-help">No cases currently assigned to you.</p>';

      el.querySelectorAll('[data-action="update-status"]').forEach((btn) => {
        btn.addEventListener("click", async () => {
          const caseId = btn.dataset.caseId;
          const status = document.getElementById(`status-${caseId}`).value;
          const resultEl = document.getElementById(`status-result-${caseId}`);
          try {
            await DEMS.request(`/api/cases/${caseId}/status`, { method: "PATCH", body: { status } });
            loadCases();
          } catch (err) {
            resultEl.innerHTML = `<div class="alert error">${DEMS.escapeHtml(err.message)}</div>`;
          }
        });
      });
    } catch (err) {
      el.innerHTML = `<div class="alert error">${DEMS.escapeHtml(err.message)}</div>`;
    }
  }

  loadCases();
})();
