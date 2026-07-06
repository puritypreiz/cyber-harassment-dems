(function () {
  DEMS.requireAuth();

  const params = new URLSearchParams(window.location.search);
  const caseId = params.get("case_id");
  const summaryEl = document.getElementById("case-summary");
  const listEl = document.getElementById("evidence-list");

  if (!caseId) {
    summaryEl.innerHTML = '<div class="alert error">No case selected. Go back to your dashboard and choose a case.</div>';
    return;
  }

  async function loadCase() {
    try {
      const data = await DEMS.request(`/api/cases/${caseId}`);
      summaryEl.innerHTML = renderCaseCard(data.case);
    } catch (err) {
      summaryEl.innerHTML = `<div class="alert error">${DEMS.escapeHtml(err.message)}</div>`;
    }
  }

  async function loadEvidence() {
    try {
      const data = await DEMS.request(`/api/cases/${caseId}/evidence`);
      if (!data.evidence.length) {
        listEl.innerHTML = '<p class="form-help">No evidence uploaded yet.</p>';
        return;
      }
      listEl.innerHTML = data.evidence
        .map((e) => `
          <div class="card">
            <p><a href="/evidence/${e.id}?case_id=${caseId}"><strong>${DEMS.escapeHtml(e.original_filename)}</strong></a></p>
            <p class="form-help">${DEMS.escapeHtml(e.mime_type)} &middot; ${(e.size_bytes / 1024).toFixed(1)} KB &middot; uploaded ${DEMS.escapeHtml(new Date(e.uploaded_at).toLocaleString())}</p>
            <p>SHA-256: <code>${DEMS.escapeHtml(e.sha256_hash)}</code></p>
          </div>
        `)
        .join("");
    } catch (err) {
      listEl.innerHTML = `<div class="alert error">${DEMS.escapeHtml(err.message)}</div>`;
    }
  }

  initEvidenceUploader("uploader-container", caseId, () => loadEvidence());

  loadCase();
  loadEvidence();
})();
