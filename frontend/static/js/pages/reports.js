(function () {
  DEMS.requireAuth();

  const params = new URLSearchParams(window.location.search);
  const prefill = params.get("case_id");
  if (prefill) document.getElementById("report-case-id").value = prefill;

  document.getElementById("report-download-btn").addEventListener("click", async () => {
    const caseId = document.getElementById("report-case-id").value.trim();
    const resultEl = document.getElementById("report-result");
    if (!caseId) {
      resultEl.innerHTML = '<div class="alert error">Enter a case ID.</div>';
      return;
    }

    resultEl.innerHTML = '<div class="alert info">Generating report...</div>';
    try {
      const res = await fetch(`/api/cases/${caseId}/report`, {
        headers: { Authorization: `Bearer ${DEMS.getAccessToken()}` },
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || "Could not generate report.");
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${caseId}_chain_of_custody.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      resultEl.innerHTML = '<div class="alert success">Report downloaded.</div>';
    } catch (err) {
      resultEl.innerHTML = `<div class="alert error">${DEMS.escapeHtml(err.message)}</div>`;
    }
  });
})();
