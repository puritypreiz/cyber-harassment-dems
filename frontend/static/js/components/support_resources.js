async function renderSupportResources(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  try {
    const [hotline, resources] = await Promise.all([
      DEMS.request("/api/support/hotline"),
      DEMS.request("/api/support/resources"),
    ]);

    container.innerHTML = `
      <div class="hotline-banner">
        If you are in immediate danger, call your local emergency number.
        National hotline: <strong>${DEMS.escapeHtml(hotline.national_hotline)}</strong> &middot; ${DEMS.escapeHtml(hotline.text_line)}
      </div>
      <div class="card">
        <h3>Support resources</h3>
        <ul>
          ${resources.resources.map((r) => `<li><strong>${DEMS.escapeHtml(r.name)}</strong> — ${DEMS.escapeHtml(r.contact)} (${DEMS.escapeHtml(r.available)})</li>`).join("")}
        </ul>
      </div>
    `;
  } catch (_err) {
    container.innerHTML = "";
  }
}
