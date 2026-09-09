const form = document.getElementById('scan-form');
const targetInput = document.getElementById('target-url');
const submitButton = document.getElementById('scan-submit');
const statusText = document.getElementById('scan-status');
const tableBody = document.getElementById('scan-table-body');
const scanEmpty = document.getElementById('scan-empty');
const detailsSection = document.getElementById('details-section');
const currentFilters = { search: '', status: 'all', severity: 'all' };
let scans = [];
let selectedScan = null;

async function fetchJson(url, options = {}) {
  const response = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...options });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Request failed.');
  return data;
}

function text(value, fallback = 'Unavailable') {
  return value === null || value === undefined || value === '' ? fallback : String(value);
}

function riskLabel(score) {
  if (score >= 75) return 'Critical';
  if (score >= 50) return 'High';
  if (score >= 25) return 'Medium';
  if (score > 0) return 'Low';
  return 'No data';
}

function riskClass(score) {
  return `risk-${riskLabel(score).toLowerCase()}`;
}

function statusBadge(status) {
  const badge = document.createElement('span');
  badge.className = `status-badge status-${status}`;
  badge.textContent = status;
  return badge;
}

function formatDate(value) {
  if (!value) return '—';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString(undefined, { month: 'short', day: '2-digit' });
}

function filteredScans() {
  return scans.filter(scan => {
    const matchesSearch = !currentFilters.search || scan.target_url.toLowerCase().includes(currentFilters.search);
    const matchesStatus = currentFilters.status === 'all' || scan.status === currentFilters.status;
    return matchesSearch && matchesStatus;
  });
}

function renderScanTable() {
  tableBody.replaceChildren();
  const visible = filteredScans();
  scanEmpty.classList.toggle('hidden', visible.length !== 0);
  document.querySelector('.table-wrap').classList.toggle('hidden', visible.length === 0);
  visible.forEach(scan => {
    const row = document.createElement('tr');
    row.className = 'scan-row';
    row.tabIndex = 0;
    row.addEventListener('click', () => displayScan(scan));
    row.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') displayScan(scan); });
    const target = document.createElement('td');
    target.className = 'target-cell';
    target.title = scan.target_url;
    target.textContent = scan.target_url;
    const status = document.createElement('td');
    status.appendChild(statusBadge(scan.status));
    const risk = document.createElement('td');
    risk.className = riskClass(scan.risk_score);
    risk.textContent = `${text(scan.risk_score, '0')} ${riskLabel(scan.risk_score)}`;
    const findings = document.createElement('td');
    findings.textContent = (scan.findings || []).length;
    const date = document.createElement('td');
    date.textContent = formatDate(scan.created_at);
    row.append(target, status, risk, findings, date);
    tableBody.appendChild(row);
  });
}

function updateStats() {
  const latest = scans[0];
  const totalPages = scans.reduce((sum, scan) => sum + ((scan.metadata || {}).crawl || {}).pages_crawled || 0, 0);
  const findings = scans.reduce((sum, scan) => sum + (scan.findings || []).length, 0);
  document.getElementById('stat-scans').textContent = scans.length;
  document.getElementById('stat-scans-note').textContent = scans.length ? `${scans.filter(scan => scan.status === 'completed').length} completed` : 'No scans yet';
  document.getElementById('stat-pages').textContent = totalPages;
  document.getElementById('stat-pages-note').textContent = scans.length ? 'Across recent scans' : 'No scans yet';
  document.getElementById('stat-findings').textContent = findings;
  document.getElementById('stat-findings-note').textContent = findings ? 'Across all scans' : 'No findings yet';
  document.getElementById('stat-risk').replaceChildren();
  const score = document.createTextNode(text(latest ? latest.risk_score : 0, '0'));
  const suffix = document.createElement('span');
  suffix.textContent = '/100';
  document.getElementById('stat-risk').append(score, suffix);
  document.getElementById('stat-risk-note').textContent = latest ? `${riskLabel(latest.risk_score)} risk` : 'No scans yet';
  document.getElementById('scan-count').textContent = scans.length;
  renderSeverityBreakdown();
}

function renderSeverityBreakdown() {
  const counts = { critical: 0, high: 0, medium: 0, low: 0, info: 0 };
  scans.forEach(scan => (scan.findings || []).forEach(finding => {
    const severity = (finding.severity || 'info').toLowerCase();
    counts[severity] = (counts[severity] || 0) + 1;
  }));
  const list = document.getElementById('severity-list');
  list.replaceChildren();
  Object.entries(counts).forEach(([severity, count]) => {
    const item = document.createElement('div');
    item.className = `severity-item ${severity}`;
    const name = document.createElement('span');
    name.className = 'severity-name';
    name.textContent = severity;
    const total = document.createElement('strong');
    total.textContent = count;
    item.append(name, total);
    list.appendChild(item);
  });
  const latest = scans[0];
  document.getElementById('risk-summary-score').firstChild.textContent = `${latest ? latest.risk_score : 0} `;
  document.getElementById('risk-summary-label').textContent = latest ? riskLabel(latest.risk_score) : 'No data';
}

function metric(label, value) {
  const item = document.createElement('div');
  item.className = 'metric';
  const name = document.createElement('span');
  name.textContent = label;
  const content = document.createElement('strong');
  content.title = text(value);
  content.textContent = text(value);
  item.append(name, content);
  return item;
}

function renderFindingCard(finding) {
  const card = document.createElement('article');
  const severity = (finding.severity || 'info').toLowerCase();
  card.className = `finding-card ${severity}`;
  const top = document.createElement('div');
  top.className = 'finding-top';
  const badge = document.createElement('span');
  badge.className = `severity-badge ${severity}`;
  badge.textContent = severity;
  const category = document.createElement('span');
  category.className = 'finding-category';
  category.textContent = text(finding.category, 'Observation');
  top.append(badge, category);
  const title = document.createElement('h4');
  title.textContent = text(finding.title, 'Finding');
  const description = document.createElement('p');
  description.className = 'finding-description';
  description.textContent = text(finding.description, finding.evidence);
  const meta = document.createElement('div');
  meta.className = 'finding-meta';
  [['Evidence', finding.evidence], ['Recommendation', finding.recommendation], ['Affected URL', finding.affected_url]].forEach(([label, value]) => {
    if (!value) return;
    const block = document.createElement('div');
    const labelNode = document.createElement('span');
    labelNode.textContent = label;
    const valueNode = document.createElement('strong');
    valueNode.textContent = value;
    block.append(labelNode, valueNode);
    meta.appendChild(block);
  });
  card.append(top, title, description, meta);
  return card;
}

function displayScan(scan) {
  selectedScan = scan;
  const metadata = scan.metadata || {};
  const target = metadata.target || {};
  const http = metadata.http || {};
  const crawl = metadata.crawl || {};
  document.getElementById('details-title').textContent = text(target.hostname, scan.target_url);
  document.getElementById('details-subtitle').textContent = `${text(target.scheme, 'unknown').toUpperCase()} · ${scan.status}`;
  const risk = document.getElementById('details-risk');
  risk.className = `risk-display ${riskClass(scan.risk_score)}`;
  risk.replaceChildren();
  const score = document.createElement('strong');
  score.textContent = text(scan.risk_score, '0');
  const scoreLabel = document.createElement('small');
  scoreLabel.textContent = `/ 100 · ${riskLabel(scan.risk_score)}`;
  risk.append(score, scoreLabel);
  const targetMetrics = document.getElementById('target-metrics');
  targetMetrics.replaceChildren();
  [['Target URL', target.url || scan.target_url], ['Hostname', target.hostname], ['IP address', target.ip_address], ['Scheme', target.scheme && target.scheme.toUpperCase()], ['HTTP status', http.status_code], ['Final URL', http.final_url]].forEach(([label, value]) => targetMetrics.appendChild(metric(label, value)));
  const reconMetrics = document.getElementById('recon-metrics');
  reconMetrics.replaceChildren(metric('Status', scan.status), metric('Summary', scan.summary));
  const headers = document.getElementById('headers-list');
  headers.replaceChildren();
  const headerEntries = Object.entries(http.headers || {});
  if (!headerEntries.length) headers.appendChild(metric('Headers', 'None collected'));
  headerEntries.forEach(([name, value]) => {
    const line = document.createElement('div');
    line.className = 'header-line';
    const key = document.createElement('span');
    key.textContent = name;
    const content = document.createElement('strong');
    content.textContent = value;
    line.append(key, content);
    headers.appendChild(line);
  });
  const crawlMetrics = document.getElementById('crawl-metrics');
  crawlMetrics.replaceChildren(metric('Pages crawled', crawl.pages_crawled || 0), metric('URLs discovered', (crawl.discovered_urls || []).length), metric('Maximum depth', crawl.max_depth || 0));
  const pages = document.getElementById('pages-list');
  pages.replaceChildren();
  (crawl.pages || []).forEach(page => {
    const line = document.createElement('div');
    line.className = 'page-line';
    const url = document.createElement('strong');
    url.title = page.url;
    url.textContent = page.url;
    const status = document.createElement('span');
    status.textContent = text(page.status_code, '—');
    const depth = document.createElement('span');
    depth.textContent = `D${text(page.depth, '—')}`;
    line.append(url, status, depth);
    pages.appendChild(line);
  });
  if (!crawl.pages || !crawl.pages.length) pages.appendChild(metric('Pages', 'None collected'));
  renderDetailFindings();
  detailsSection.classList.remove('hidden');
  detailsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderDetailFindings() {
  if (!selectedScan) return;
  const list = document.getElementById('details-findings');
  list.replaceChildren();
  const visible = (selectedScan.findings || []).filter(finding => currentFilters.severity === 'all' || (finding.severity || 'info').toLowerCase() === currentFilters.severity);
  if (!visible.length) {
    const empty = document.createElement('div');
    empty.className = 'empty-state';
    empty.textContent = 'No findings match this filter.';
    list.appendChild(empty);
    return;
  }
  visible.forEach(finding => list.appendChild(renderFindingCard(finding)));
}

async function loadScans() {
  const data = await fetchJson('/api/scans');
  scans = data.scans || [];
  updateStats();
  renderScanTable();
  if (scans.length) displayScan(scans[0]);
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  const target = targetInput.value.trim();
  if (!target) { statusText.textContent = 'Please enter a valid URL.'; return; }
  submitButton.disabled = true;
  statusText.textContent = 'Scanning target... reconnaissance and passive checks in progress.';
  try {
    const created = await fetchJson('/api/scans', { method: 'POST', body: JSON.stringify({ target }) });
    const result = await fetchJson(`/api/scans/${created.scan.id}/run`, { method: 'POST' });
    await loadScans();
    displayScan(result.scan);
    statusText.textContent = `Scan finished for ${result.scan.target_url}.`;
    form.reset();
  } catch (error) {
    statusText.textContent = error.message;
  } finally {
    submitButton.disabled = false;
  }
});

document.getElementById('scan-search').addEventListener('input', event => { currentFilters.search = event.target.value.trim().toLowerCase(); renderScanTable(); });
document.getElementById('status-filter').addEventListener('change', event => { currentFilters.status = event.target.value; renderScanTable(); });
document.getElementById('back-to-scans').addEventListener('click', () => document.getElementById('scans').scrollIntoView({ behavior: 'smooth' }));
document.querySelectorAll('[data-action="focus-scan"]').forEach(button => button.addEventListener('click', () => targetInput.focus()));
document.querySelectorAll('[data-severity]').forEach(button => button.addEventListener('click', () => {
  currentFilters.severity = button.dataset.severity;
  document.querySelectorAll('[data-severity]').forEach(item => item.classList.toggle('active', item === button));
  renderDetailFindings();
}));

loadScans().catch(error => { statusText.textContent = error.message; });
