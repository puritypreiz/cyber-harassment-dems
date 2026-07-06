function renderTimeline(containerId, entries) {
  const container = document.getElementById(containerId);
  if (!container) return;

  if (!entries.length) {
    container.innerHTML = '<p class="form-help">No activity recorded yet.</p>';
    return;
  }

  container.innerHTML = entries
    .map((entry) => `
      <div class="timeline-item">
        <div class="ts">${DEMS.escapeHtml(new Date(entry.timestamp).toLocaleString())}</div>
        <div><strong>${DEMS.escapeHtml(entry.action.replace(/_/g, " "))}</strong></div>
      </div>
    `)
    .join("");
}
