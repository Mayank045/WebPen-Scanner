const form = document.getElementById('scan-form');
const targetInput = document.getElementById('target-url');
const statusText = document.getElementById('scan-status');
const scanList = document.getElementById('scan-list');
const resultDetails = document.getElementById('result-details');

async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Request failed.');
  }
  return data;
}

function renderScanList(scans) {
  scanList.innerHTML = '';
  if (!scans.length) {
    scanList.innerHTML = '<li class="scan-item"><small>No scans yet.</small></li>';
    return;
  }

  scans.forEach(scan => {
    const item = document.createElement('li');
    item.className = 'scan-item';
    item.innerHTML = `
      <strong>${scan.target_url}</strong>
      <small>${scan.status} · Risk ${scan.risk_score}</small>
    `;
    item.addEventListener('click', () => displayScan(scan));
    scanList.appendChild(item);
  });
}

function renderFindings(findings = []) {
  if (!findings.length) {
    return '<p>No findings reported.</p>';
  }

  return findings.map(f => `
    <li class="finding">
      <span class="tag ${f.severity}">${f.severity}</span>
      <strong>${f.title}</strong>
      <div>${f.evidence}</div>
    </li>
  `).join('');
}

function displayScan(scan) {
  const findings = scan.findings || [];
  const recon = scan.metadata || {};
  const target = recon.target || {};
  const http = recon.http || {};
  const headers = http.headers || {};
  const headerMarkup = Object.entries(headers).map(([name, value]) => `
    <div class="metric"><span>${name}</span><strong>${value}</strong></div>
  `).join('');
  resultDetails.className = 'result-details';
  resultDetails.innerHTML = `
    <div>
      <h3>${target.url || scan.target_url}</h3>
      <div class="score">${scan.risk_score}</div>
      <small>Risk score</small>
    </div>
    <div class="recon-grid">
      <div class="metric"><span>Hostname</span><strong>${target.hostname || 'Unavailable'}</strong></div>
      <div class="metric"><span>IP address</span><strong>${target.ip_address || 'Unavailable'}</strong></div>
      <div class="metric"><span>Scheme</span><strong>${(target.scheme || 'unknown').toUpperCase()}</strong></div>
      <div class="metric"><span>HTTP status</span><strong>${http.status_code || 'Unavailable'}</strong></div>
      <div class="metric"><span>Final URL</span><strong>${http.final_url || 'Unavailable'}</strong></div>
    </div>
    <div>
      <h3>Response headers</h3>
      ${headerMarkup || '<p>No response headers available.</p>'}
    </div>
    <div class="metric"><span>Status</span><strong>${scan.status}</strong></div>
    <div class="metric"><span>Summary</span><strong>${scan.summary || 'No summary available.'}</strong></div>
    <div>
      <h3>Findings</h3>
      <ul class="findings">${renderFindings(findings)}</ul>
    </div>
  `;
}

async function loadScans() {
  const data = await fetchJson('/api/scans');
  renderScanList(data.scans || []);
  if (data.scans && data.scans.length) {
    displayScan(data.scans[0]);
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const target = targetInput.value.trim();
  if (!target) {
    statusText.textContent = 'Please enter a valid URL.';
    return;
  }

  statusText.textContent = 'Creating scan...';
  try {
    const created = await fetchJson('/api/scans', {
      method: 'POST',
      body: JSON.stringify({ target })
    });

    const scan = created.scan;
    statusText.textContent = `Scan created for ${scan.target_url}. Starting analysis...`;

    const runResult = await fetchJson(`/api/scans/${scan.id}/run`, { method: 'POST' });
    displayScan(runResult.scan);
    await loadScans();
    statusText.textContent = `Scan finished for ${scan.target_url}.`;
  } catch (error) {
    statusText.textContent = error.message;
  }
});

loadScans();
