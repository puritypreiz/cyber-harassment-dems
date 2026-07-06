function initEvidenceUploader(containerId, caseId, onUploaded) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = `
    <div class="card">
      <h3>Upload evidence</h3>
      <label for="ev-file">File (screenshot, message export, recording, etc.)</label>
      <input type="file" id="ev-file" />
      <label for="ev-description">Description (optional)</label>
      <textarea id="ev-description" rows="2" placeholder="e.g. Screenshot of harassing messages from Instagram, received 2026-06-30"></textarea>
      <button id="ev-upload-btn" class="btn" style="margin-top:0.5rem;">Upload</button>
      <div id="ev-upload-result" style="margin-top:0.75rem;"></div>
    </div>
  `;

  const resultEl = container.querySelector("#ev-upload-result");

  container.querySelector("#ev-upload-btn").addEventListener("click", async () => {
    const fileInput = container.querySelector("#ev-file");
    const description = container.querySelector("#ev-description").value;
    if (!fileInput.files.length) {
      resultEl.innerHTML = '<div class="alert error">Choose a file first.</div>';
      return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    if (description) formData.append("description", description);

    resultEl.innerHTML = '<div class="alert info">Uploading and encrypting...</div>';
    try {
      const data = await DEMS.request(`/api/cases/${caseId}/evidence`, { method: "POST", body: formData });
      resultEl.innerHTML = '<div class="alert success">Evidence uploaded and encrypted successfully.</div>';
      fileInput.value = "";
      if (onUploaded) onUploaded(data.evidence);
    } catch (err) {
      resultEl.innerHTML = `<div class="alert error">${DEMS.escapeHtml(err.message)}</div>`;
    }
  });
}
