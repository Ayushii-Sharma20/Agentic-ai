// background.js — service worker

const API_BASE = 'http://localhost:8000/api/v2';

// ─────────────────────────────────────────────
// Context menu
// ─────────────────────────────────────────────
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'analyzeSelection',
    title: 'Analyze with Terms Analyzer',
    contexts: ['selection'],
  });

  chrome.contextMenus.create({
    id: 'analyzePage',
    title: 'Analyze This Page',
    contexts: ['page'],
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === 'analyzeSelection') {
    const text = info.selectionText;
    if (!text || text.length < 100) {
      showNotification('Too Short', 'Please select more text (at least 100 characters).');
      return;
    }
    await analyzeAndShow(tab, text);
  }

  if (info.menuItemId === 'analyzePage') {
    const [{ result: pageText }] = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => document.body.innerText,
    });
    await analyzeAndShow(tab, pageText?.slice(0, 50000) || '', tab.url);
  }
});

// ─────────────────────────────────────────────
// Analyze and inject results into page
// ─────────────────────────────────────────────
async function analyzeAndShow(tab, text, url = '') {
  try {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, url }),
    });

    if (!res.ok) throw new Error(`API error ${res.status}`);

    const data = await res.json();

    // Show banner in page
    chrome.tabs.sendMessage(tab.id, { action: 'SHOW_BANNER', data });

    // If high/medium risk, highlight clauses
    if (data.risk_level !== 'Low') {
      chrome.tabs.sendMessage(tab.id, {
        action: 'HIGHLIGHT_CLAUSES',
        clauses: data.clauses,
      });
    }

    // Store result
    await storeResult(url || tab.url, data);

  } catch (err) {
    showNotification('Analysis Failed', err.message || 'Could not reach backend.');
  }
}

// ─────────────────────────────────────────────
// Storage helpers
// ─────────────────────────────────────────────
async function storeResult(url, result) {
  const { recentAnalyses = [] } = await chrome.storage.local.get('recentAnalyses');
  const entry = { url, risk_level: result.risk_level, result, timestamp: Date.now() };
  const filtered = recentAnalyses.filter(r => r.url !== url);
  await chrome.storage.local.set({
    recentAnalyses: [entry, ...filtered].slice(0, 20),
  });
}

// ─────────────────────────────────────────────
// Notification
// ─────────────────────────────────────────────
function showNotification(title, message) {
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'assets/icons/icon48.png',
    title: `Terms Analyzer: ${title}`,
    message,
  });
}

// ─────────────────────────────────────────────
// Message relay from popup
// ─────────────────────────────────────────────
chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.action === 'CHECK_API') {
    fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(3000) })
      .then(r => sendResponse({ ok: r.ok }))
      .catch(() => sendResponse({ ok: false }));
    return true; // async
  }
});