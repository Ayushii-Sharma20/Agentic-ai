// content.js — injected into every page

(function () {
  'use strict';

  let tooltip = null;

  // ─────────────────────────────────────
  // Message listener from popup / background
  // ─────────────────────────────────────
  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    switch (message.action) {
      case 'HIGHLIGHT_CLAUSES':
        highlightClauses(message.clauses || []);
        sendResponse({ success: true });
        break;

      case 'SHOW_BANNER':
        showResultBanner(message.data);
        sendResponse({ success: true });
        break;

      case 'GET_PAGE_TEXT':
        sendResponse({ text: document.body.innerText });
        break;

      case 'CLEAR_HIGHLIGHTS':
        clearHighlights();
        sendResponse({ success: true });
        break;

      default:
        break;
    }
  });

  // ─────────────────────────────────────
  // Highlighting
  // ─────────────────────────────────────
  function highlightClauses(clauses) {
    clearHighlights();

    clauses.forEach(clause => {
      if (!clause.text) return;
      highlightText(clause.text, clause.risk_level, clause.category, clause.explanation);
    });
  }

  function highlightText(searchText, riskLevel, category, explanation) {
    const snippet = searchText.slice(0, 80).trim();
    if (!snippet) return;

    const walker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode(node) {
          if (['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(node.parentElement?.tagName)) {
            return NodeFilter.FILTER_REJECT;
          }
          return node.textContent.includes(snippet.slice(0, 40))
            ? NodeFilter.FILTER_ACCEPT
            : NodeFilter.FILTER_SKIP;
        },
      }
    );

    const nodes = [];
    let node;
    while ((node = walker.nextNode())) nodes.push(node);

    nodes.forEach(textNode => {
      const idx = textNode.textContent.indexOf(snippet.slice(0, 40));
      if (idx === -1) return;

      const range = document.createRange();
      range.setStart(textNode, idx);
      range.setEnd(textNode, Math.min(idx + searchText.length, textNode.length));

      const mark = document.createElement('mark');
      mark.className = `tc-analyzer-highlight ${(riskLevel || 'medium').toLowerCase()}`;
      mark.dataset.category = category;
      mark.dataset.explanation = explanation;
      mark.dataset.risk = riskLevel;

      try {
        range.surroundContents(mark);
        addTooltipListeners(mark);
      } catch {
        // Range spans multiple elements — skip
      }
    });
  }

  function clearHighlights() {
    document.querySelectorAll('.tc-analyzer-highlight').forEach(mark => {
      const parent = mark.parentNode;
      if (parent) {
        parent.replaceChild(document.createTextNode(mark.textContent), mark);
        parent.normalize();
      }
    });
    removeTooltip();
  }

  // ─────────────────────────────────────
  // Tooltip
  // ─────────────────────────────────────
  function addTooltipListeners(mark) {
    mark.addEventListener('mouseenter', e => showTooltip(e, mark));
    mark.addEventListener('mouseleave', removeTooltip);
  }

  function showTooltip(e, mark) {
    removeTooltip();
    tooltip = document.createElement('div');
    tooltip.className = 'tc-tooltip';
    tooltip.innerHTML = `
      <div class="tc-tooltip-category ${mark.dataset.risk}">${mark.dataset.category}</div>
      <div class="tc-tooltip-explanation">${mark.dataset.explanation}</div>
    `;
    document.body.appendChild(tooltip);
    positionTooltip(e);
  }

  function positionTooltip(e) {
    if (!tooltip) return;
    const x = Math.min(e.clientX + 12, window.innerWidth - 300);
    const y = Math.min(e.clientY + 16, window.innerHeight - 120);
    tooltip.style.left = `${x}px`;
    tooltip.style.top = `${y}px`;
  }

  function removeTooltip() {
    if (tooltip) {
      tooltip.remove();
      tooltip = null;
    }
  }

  // ─────────────────────────────────────
  // Result banner
  // ─────────────────────────────────────
  function showResultBanner(data) {
    const existing = document.getElementById('tc-result-banner');
    if (existing) existing.remove();

    const icons = { High: '🔴', Medium: '🟡', Low: '🟢' };
    const level = data?.risk_level || 'Low';

    const banner = document.createElement('div');
    banner.id = 'tc-result-banner';
    banner.className = `tc-banner ${level.toLowerCase()}`;
    banner.innerHTML = `
      <span class="tc-banner-icon">${icons[level]}</span>
      <div class="tc-banner-content">
        <div class="tc-banner-title">${level} Risk · ${data?.recommendation || ''}</div>
        <div class="tc-banner-body">Score: ${data?.risk_score || 0}/100 · ${data?.clauses?.length || 0} clauses detected</div>
      </div>
      <button class="tc-banner-close" id="tc-banner-close-btn">×</button>
    `;

    document.body.appendChild(banner);

    document.getElementById('tc-banner-close-btn').addEventListener('click', () => {
      banner.remove();
    });

    // Auto-dismiss after 8 seconds
    setTimeout(() => banner?.remove(), 8000);
  }
})();