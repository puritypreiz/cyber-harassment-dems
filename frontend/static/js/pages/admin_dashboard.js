(function () {
  DEMS.requireAuth();
  DEMS.requireRole("admin");

  async function loadUsers() {
    const el = document.getElementById("user-list");
    try {
      const data = await DEMS.request("/api/admin/users");
      el.innerHTML = `
        <table>
          <thead><tr><th>Username</th><th>Role</th><th>MFA</th><th>Joined</th></tr></thead>
          <tbody>
            ${data.users.map((u) => `
              <tr>
                <td>${DEMS.escapeHtml(u.username)}</td>
                <td>${DEMS.escapeHtml(u.role)}</td>
                <td>${u.mfa_enabled ? "Yes" : "No"}</td>
                <td>${DEMS.escapeHtml(new Date(u.created_at).toLocaleDateString())}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      `;
    } catch (err) {
      el.innerHTML = `<div class="alert error">${DEMS.escapeHtml(err.message)}</div>`;
    }
  }

  async function loadAuditLog() {
    const el = document.getElementById("audit-log-table");
    try {
      const data = await DEMS.request("/api/admin/audit-log?per_page=25");
      el.innerHTML = `
        <table>
          <thead><tr><th>Time</th><th>Action</th><th>Entity</th></tr></thead>
          <tbody>
            ${data.entries.map((e) => `
              <tr>
                <td>${DEMS.escapeHtml(new Date(e.created_at).toLocaleString())}</td>
                <td>${DEMS.escapeHtml(e.action)}</td>
                <td>${DEMS.escapeHtml(e.entity_type || "")}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      `;
    } catch (err) {
      el.innerHTML = `<div class="alert error">${DEMS.escapeHtml(err.message)}</div>`;
    }
  }

  document.getElementById("verify-chain-btn").addEventListener("click", async () => {
    const el = document.getElementById("chain-result");
    el.innerHTML = '<div class="alert info">Verifying signatures and hash chain...</div>';
    try {
      const data = await DEMS.request("/api/admin/audit-log/verify");
      const allValid = data.results.every((r) => r.signature_valid && r.chain_linkage_valid);
      el.innerHTML = allValid
        ? `<div class="alert success">All ${data.results.length} audit entries verified: signatures and chain linkage intact.</div>`
        : `<div class="alert error">Integrity issue detected in the audit trail. Review immediately.</div>`;
    } catch (err) {
      el.innerHTML = `<div class="alert error">${DEMS.escapeHtml(err.message)}</div>`;
    }
  });

  async function loadRetentionCandidates() {
    const el = document.getElementById("retention-list");
    try {
      const data = await DEMS.request("/api/admin/retention/review-candidates");
      el.innerHTML = data.cases.length
        ? data.cases.map((c) => `<p>#${DEMS.escapeHtml(c.case_number)} — ${DEMS.escapeHtml(c.title)} (closed ${DEMS.escapeHtml(c.updated_at)})</p>`).join("")
        : '<p class="form-help">No cases are currently due for retention review.</p>';
    } catch (err) {
      el.innerHTML = `<div class="alert error">${DEMS.escapeHtml(err.message)}</div>`;
    }
  }

  loadUsers();
  loadAuditLog();
  loadRetentionCandidates();
})();
