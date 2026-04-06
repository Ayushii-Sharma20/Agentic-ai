// popup.js — main popup controller

// Page state
let currentPage = 'home';
let currentAnalysis = null;
let currentTab = null;

// DOM refs
const pages = {
  home: document.getElementById('homePage'),
  loading: document.getElementById('loadingPage'),
  results: document.getElementById('resultsPage'),
  error: document.getElementById('errorPage'),
};

// ──────────────────────────────────────────
// Init
// ──────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  currentTab = await getCurrentTab();

  updatePageInfo();
  updateAnalyzeButtons();
  checkApiStatus();
  loadRecentAnalyses();
  setupEventListeners();
  checkForSelectedText();
});

function updateAnalyzeButtons() {
  const disabled = !isValidTab(currentTab);
  document.getElementById('analyzePageBtn').disabled = disabled;
  document.getElementById('analyzeSelectedBtn').disabled = disabled || document.getElementById('analyzeSelectedBtn').disabled;
}

async function getCurrentTab() {
  return new Promise(resolve => {
    chrome.tabs.query({ active: true, lastFocusedWindow: true }, tabs => resolve(tabs?.[0] || null));
  });
}

function isValidTab(tab) {
  return tab && typeof tab.id === 'number' && tab.id >= 0;
}

// ──────────────────────────────────────────
// UI helpers
// ──────────────────────────────────────────
function showPage(name) {
  Object.entries(pages).forEach(([key, el]) => {
    el.classList.toggle('hidden', key !== name);
  });
  currentPage = name;
}

function updatePageInfo() {
  if (!currentTab) return;
  const urlEl = document.getElementById('pageUrl');
  const typeEl = document.getElementById('pageType');
  urlEl.textContent = currentTab.url || '';
  const url = (currentTab.url || '').toLowerCase();
  if (url.includes('privacy') || url.includes('policy')) {
    typeEl.textContent = '🔒 Privacy Policy detected';
  } else if (url.includes('terms') || url.includes('tos') || url.includes('legal')) {
    typeEl.textContent = '📄 Terms of Service detected';
  } else {
    typeEl.textContent = '';
  }
}

async function checkApiStatus() {
  const dot = document.getElementById('statusDot');
  dot.className = 'status-dot checking';
  try {
    const res = await ApiUtil.health();
    dot.className = res.status === 'healthy' ? 'status-dot online' : 'status-dot offline';
  } catch {
    dot.className = 'status-dot offline';
  }
}

function setLoadingStep(step) {
  // step: 1, 2, or 3
  for (let i = 1; i <= 3; i++) {
    const el = document.getElementById(`step${i}`);
    if (i < step) el.className = 'step done';
    else if (i === step) el.className = 'step active';
    else el.className = 'step';
  }
}

// ──────────────────────────────────────────
// Analysis
// ──────────────────────────────────────────
async function runAnalysis(text, url = '') {
  showPage('loading');
  setLoadingStep(1);

  try {
    // Simulate step progression while waiting
    setTimeout(() => setLoadingStep(2), 1200);
    setTimeout(() => setLoadingStep(3), 2800);

    const result = await analyzeText(text, url);
    currentAnalysis = result;

    await saveAnalysis(url || currentTab?.url || '', result);
    loadRecentAnalyses();

    renderResults(result);
    showPage('results');
  } catch (err) {
    document.getElementById('errorMessage').textContent =
      err.message || 'An error occurred. Make sure the backend is running.';
    showPage('error');
  }
}

async function analyzeText(text, url) {
  return ApiUtil.analyze(text, url);
}

// ──────────────────────────────────────────
// Render results
// ──────────────────────────────────────────
function renderResults(data) {
  const level = data.risk_level; // "High" | "Medium" | "Low"
  const banner = document.getElementById('riskBanner');
  const icons = { High: '🔴', Medium: '🟡', Low: '🟢' };
  const bannerClass = { High: 'high', Medium: 'medium', Low: 'low' };

  banner.className = `risk-banner ${bannerClass[level]}`;
  document.getElementById('riskIcon').textContent = icons[level];
  document.getElementById('riskLevel').textContent = `${level} Risk`;
  document.getElementById('riskRecommendation').textContent = data.recommendation;
  document.getElementById('riskScore').textContent = `${data.risk_score}`;

  document.getElementById('summaryText').textContent = data.summary;

  // Key concerns
  const concernsList = document.getElementById('concernsList');
  if (data.key_concerns?.length) {
    concernsList.innerHTML = data.key_concerns
      .map(c => `<li class="concern-item">⚠️ ${c}</li>`)
      .join('');
    document.getElementById('concernsSection').classList.remove('hidden');
  } else {
    document.getElementById('concernsSection').classList.add('hidden');
  }

  // Clauses
  document.getElementById('clauseCount').textContent = data.clauses?.length || 0;
  const clausesList = document.getElementById('clausesList');
  clausesList.innerHTML = '';

  (data.clauses || []).forEach((clause, i) => {
    const el = document.createElement('div');
    el.className = 'clause-item';
    el.innerHTML = `
      <div class="clause-header">
        <span class="clause-category">${clause.category}</span>
        <span class="clause-risk ${clause.risk_level}">${clause.risk_level}</span>
      </div>
      <div class="clause-explanation">${clause.explanation}</div>
      <div class="clause-text">"${truncate(clause.text, 200)}"</div>
      <div class="clause-confidence">${Math.round(clause.confidence * 100)}% confidence</div>
    `;
    el.addEventListener('click', () => el.classList.toggle('expanded'));
    clausesList.appendChild(el);
  });
}

function truncate(str, max) {
  return str.length > max ? str.slice(0, max) + '…' : str;
}

// ──────────────────────────────────────────
// Recent analyses
// ──────────────────────────────────────────
async function loadRecentAnalyses() {
  const recent = await StorageUtil.getRecent();
  const list = document.getElementById('recentList');
  const section = document.getElementById('recentSection');

  if (!recent.length) {
    section.classList.add('hidden');
    return;
  }

  section.classList.remove('hidden');
  list.innerHTML = recent
    .slice(0, 3)
    .map(item => {
      const domain = extractDomain(item.url);
      const badgeClass = item.risk_level?.toLowerCase() || 'low';
      return `
        <div class="recent-item" data-url="${item.url}">
          <span class="recent-domain">${domain}</span>
          <span class="recent-badge badge-${badgeClass}">${item.risk_level || '?'}</span>
        </div>
      `;
    })
    .join('');

  list.querySelectorAll('.recent-item').forEach(el => {
    el.addEventListener('click', async () => {
      const cached = await StorageUtil.getByUrl(el.dataset.url);
      if (cached) {
        currentAnalysis = cached.result;
        renderResults(cached.result);
        showPage('results');
      }
    });
  });
}

async function saveAnalysis(url, result) {
  await StorageUtil.save({
    url,
    risk_level: result.risk_level,
    result,
    timestamp: Date.now(),
  });
}

function extractDomain(url) {
  try {
    return new URL(url).hostname.replace('www.', '');
  } catch {
    return url || 'Unknown';
  }
}

// ──────────────────────────────────────────
// Event listeners
// ──────────────────────────────────────────
function setupEventListeners() {
  // Analyze page
  document.getElementById('analyzePageBtn').addEventListener('click', async () => {
    try {
      if (!isValidTab(currentTab)) {
        throw new Error('Cannot access the current page. Open this popup from a normal browser tab.');
      }

      const [{ result }] = await chrome.scripting.executeScript({
        target: { tabId: currentTab.id },
        func: () => document.body.innerText,
      });
      if (!result || result.length < 100) {
        throw new Error('Not enough text found on this page. Try selecting text manually.');
      }
      await runAnalysis(result.slice(0, 50000), currentTab.url);
    } catch (err) {
      document.getElementById('errorMessage').textContent = err?.message || 'An unexpected error occurred.';
      showPage('error');
    }
  });

  // Analyze selected text
  document.getElementById('analyzeSelectedBtn').addEventListener('click', async () => {
    try {
      if (!isValidTab(currentTab)) {
        throw new Error('Cannot access the current page. Open this popup from a normal browser tab.');
      }
      const [{ result }] = await chrome.scripting.executeScript({
        target: { tabId: currentTab.id },
        func: () => window.getSelection()?.toString() || '',
      });
      if (!result || result.length < 100) {
        throw new Error('Selected text is too short. Please select more text.');
      }
      await runAnalysis(result, currentTab.url);
    } catch (err) {
      document.getElementById('errorMessage').textContent = err.message;
      showPage('error');
    }
  });

  // Analyze pasted text
  document.getElementById('analyzePasteBtn').addEventListener('click', async () => {
    const text = document.getElementById('pasteText').value.trim();
    if (!text || text.length < 100) {
      alert('Please paste at least 100 characters of text.');
      return;
    }
    await runAnalysis(text);
  });

  // Back button
  document.getElementById('backBtn').addEventListener('click', () => showPage('home'));

  // Retry
  document.getElementById('retryBtn').addEventListener('click', () => showPage('home'));

  // Highlight on page
  document.getElementById('highlightBtn').addEventListener('click', async () => {
    if (!currentAnalysis || !currentTab) return;
    chrome.tabs.sendMessage(currentTab.id, {
      action: 'HIGHLIGHT_CLAUSES',
      clauses: currentAnalysis.clauses,
    });
    window.close();
  });
}

async function checkForSelectedText() {
  if (!currentTab) return;
  try {
    const [{ result }] = await chrome.scripting.executeScript({
      target: { tabId: currentTab.id },
      func: () => window.getSelection()?.toString() || '',
    });
    if (result && result.length >= 100) {
      document.getElementById('analyzeSelectedBtn').disabled = false;
    }
  } catch {
    // Ignore errors (e.g., on chrome:// pages)
  }
}