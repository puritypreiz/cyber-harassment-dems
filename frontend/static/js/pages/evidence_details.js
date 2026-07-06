(function () {
  DEMS.requireAuth();

  const detailEl = document.getElementById("evidence-detail");
  const evidenceId = detailEl.dataset.evidenceId;
  const params = new URLSearchParams(window.location.search);
  const caseId = params.get("case_id");

  if (!caseId) {
    detailEl.innerHTML = '<div class="alert error">Missing case reference. Open this evidence item from your dashboard.</div>';
    return;
  }

  const basePath = `/api/cases/${caseId}/evidence/${evidenceId}`;

  async function loadEvidence() {
    try {
      const data = await DEMS.request(basePath);
      const e = data.evidence;
      detailEl.innerHTML = `
        <p><strong>${DEMS.escapeHtml(e.original_filename)}</strong></p>
        <p class="form-help">${DEMS.escapeHtml(e.mime_type)} &middot; ${(e.size_bytes / 1024).toFixed(1)} KB</p>
        <p>SHA-256: <code>${DEMS.escapeHtml(e.sha256_hash)}</code></p>
        <p>Integrity status: ${e.is_verified ? '<span class="badge severity-low">verified</span>' : '<span class="badge severity-critical">FAILED</span>'}</p>
        <p class="form-help">${DEMS.escapeHtml(e.description || "")}</p>
      `;
      await loadQrImage(e.id, e.original_filename);
    } catch (err) {
      detailEl.innerHTML = `<div class="alert error">${DEMS.escapeHtml(err.message)}</div>`;
    }
  }

  async function loadQrImage(id, filename) {
    const qrEl = document.getElementById("qr-preview");
    try {
      const res = await fetch(`/api/qr/evidence/${id}/image`, {
        headers: { Authorization: `Bearer ${DEMS.getAccessToken()}` },
      });
      if (!res.ok) throw new Error("QR code not available.");
      const blob = await res.blob();
      qrEl.innerHTML = `<img src="${URL.createObjectURL(blob)}" alt="QR code for evidence ${DEMS.escapeHtml(filename)}" />`;
    } catch (_err) {
      qrEl.innerHTML = '<p class="form-help">QR code not available.</p>';
    }
  }

  document.getElementById("verify-btn").addEventListener("click", async () => {
    const resultEl = document.getElementById("verify-result");
    resultEl.innerHTML = '<div class="alert info">Re-verifying integrity...</div>';
    try {
      const data = await DEMS.request(`${basePath}/verify`, { method: "POST" });
      resultEl.innerHTML = data.is_verified
        ? '<div class="alert success">Integrity verified: file matches its original hash.</div>'
        : '<div class="alert error">Integrity check FAILED - this file no longer matches its original hash.</div>';
      loadEvidence();
    } catch (err) {
      resultEl.innerHTML = `<div class="alert error">${DEMS.escapeHtml(err.message)}</div>`;
    }
  });

  document.getElementById("download-btn").addEventListener("click", async () => {
    try {
      const res = await fetch(`${basePath}/download`, {
        headers: { Authorization: `Bearer ${DEMS.getAccessToken()}` },
      });
      if (!res.ok) throw new Error("Download failed.");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      document.getElementById("verify-result").innerHTML = `<div class="alert error">${DEMS.escapeHtml(err.message)}</div>`;
    }
  });

  initQrScanner("qr-scanner-container", async (token, resultEl) => {
    resultEl.innerHTML = '<div class="alert info">Verifying...</div>';
    try {
      const data = await DEMS.request("/api/qr/verify", { method: "POST", body: { token } });
      resultEl.innerHTML = data.hash_matches_current_file
        ? '<div class="alert success">QR signature valid and file hash matches current evidence.</div>'
        : '<div class="alert error">QR signature is valid, but the file hash no longer matches - possible tampering.</div>';
    } catch (err) {
      resultEl.innerHTML = `<div class="alert error">${DEMS.escapeHtml(err.message)}</div>`;
    }
  });

  loadEvidence();
})();
