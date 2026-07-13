function severityBadge(severity) {
  return `<span class="badge severity-${severity}">${severity}</span>`;
}

function statusBadge(status) {
  return `<span class="badge status-${status}">${status.replace(/_/g, " ")}</span>`;
}

function renderCaseCard(caseItem) {
  return `
    <div class="card">
      <h3><a href="/cases/${caseItem.id}">${DEMS.escapeHtml(caseItem.title)}</a></h3>
      <p>${statusBadge(caseItem.status)} ${severityBadge(caseItem.severity)}</p>
      <p class="form-help">Case #${DEMS.escapeHtml(caseItem.case_number)} &middot; Category: ${DEMS.escapeHtml(caseItem.category)}</p>
    </div>
  `;
}