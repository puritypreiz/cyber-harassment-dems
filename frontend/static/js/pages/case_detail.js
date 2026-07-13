(function () {
  DEMS.requireAuth();

  const summaryEl = document.getElementById("case-summary");
  const caseId = summaryEl.dataset.caseId;
  const user = DEMS.getUser();
  const canUpdateStatus = user && ["counselor", "legal", "admin"].includes(user.role);

  const STATUS_OPTIONS = ["open", "under_review", "escalated", "resolved", "closed"];

  async function loadCase() {
    try {
      const data = await DEMS.request(`/api/cases/${caseId}`);
      const c = data.case;
      summaryEl.innerHTML = `
        <h1>${DEMS.escapeHtml(c.title)}</h1>
        <p>${statusBadge(c.status)} ${severityBadge(c.severity)}</p>
        <p class="form-help">Case #${DEMS.escapeHtml(c.case_number)} &middot; Category: ${DEMS.escapeHtml(c.category)}${c.is_anonymous ? " &middot; Filed anonymously" : ""}</p>
        <p>${DEMS.escapeHtml(c.description)}</p>
      `;
      renderStatusSection(c);
    } catch (err) {
      summaryEl.innerHTML = `<div class="alert error">${DEMS.escapeHtml(err.message)}</div>`;
    }
  }

  function renderStatusSection(c) {
    const el = document.getElementById("status-section");
    if (!canUpdateStatus) {
      el.classList.add("hidden");
      return;
    }
    el.innerHTML = `
      <h2>Update status</h2>
      <select id="status-select">
        ${STATUS_OPTIONS.map((s) => `<option value="${s}" ${s === c.status ? "selected" : ""}>${s}</option>`).join("")}
      </select>
      <button id="status-save-btn" class="btn" style="margin-top:0.5rem;">Save status</button>
      <div id="status-result" style="margin-top:0.5rem;"></div>
    `;
    document.getElementById("status-save-btn").addEventListener("click", async () => {
      const resultEl = document.getElementById("status-result");
      const status = document.getElementById("status-select").value;
      try {
        await DEMS.request(`/api/cases/${caseId}/status`, { method: "PATCH", body: { status } });
        resultEl.innerHTML = '<div class="alert success">Status updated.</div>';
        loadCase();
      } catch (err) {
        resultEl.innerHTML = `<div class="alert error">${DEMS.escapeHtml(err.message)}</div>`;
      }
    });
  }

  async function loadEvidence() {
    const el = document.getElementById("evidence-list");
    try {
      const data = await DEMS.request(`/api/cases/${caseId}/evidence`);
      el.innerHTML = data.evidence.length
        ? data.evidence.map((e) => `
            <div class="card">
              <p><a href="/evidence/${e.id}?case_id=${caseId}"><strong>${DEMS.escapeHtml(e.original_filename)}</strong></a></p>
              <p class="form-help">${DEMS.escapeHtml(e.mime_type)} &middot; uploaded ${DEMS.escapeHtml(new Date(e.uploaded_at).toLocaleString())}</p>
            </div>
          `).join("")
        : '<p class="form-help">No evidence uploaded yet.</p>';
    } catch (err) {
      el.innerHTML = `<div class="alert error">${DEMS.escapeHtml(err.message)}</div>`;
    }
  }

  async function loadTimeline() {
    try {
      const data = await DEMS.request(`/api/cases/${caseId}/timeline`);
      renderTimeline("case-timeline", data.timeline);
    } catch (err) {
      document.getElementById("case-timeline").innerHTML = `<div class="alert error">${DEMS.escapeHtml(err.message)}</div>`;
    }
  }

  loadCase();
  loadEvidence();
  loadTimeline();
})();