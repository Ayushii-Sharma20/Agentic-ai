// utils/dom.js — DOM helper utilities

const DomUtil = {
  /**
   * Extract meaningful text from a page, filtering nav/footer/scripts
   */
  extractPageText() {
    const skip = ['SCRIPT', 'STYLE', 'NOSCRIPT', 'NAV', 'FOOTER', 'HEADER', 'ASIDE'];
    const elements = document.querySelectorAll('p, li, h1, h2, h3, h4, div, article, section, main');
    const parts = [];

    elements.forEach(el => {
      if (skip.includes(el.tagName)) return;
      if (el.closest('nav, footer, header, aside')) return;
      const text = el.innerText?.trim();
      if (text && text.length > 30) parts.push(text);
    });

    return [...new Set(parts)].join('\n').slice(0, 100000);
  },

  /**
   * Detect if the current page is likely a T&C or Privacy Policy
   */
  isTermsPage() {
    const url = window.location.href.toLowerCase();
    const title = document.title.toLowerCase();
    const keywords = ['privacy', 'terms', 'tos', 'legal', 'policy', 'conditions', 'gdpr'];
    return keywords.some(k => url.includes(k) || title.includes(k));
  },

  /**
   * Inject a style tag if not already present
   */
  injectStyle(id, css) {
    if (document.getElementById(id)) return;
    const style = document.createElement('style');
    style.id = id;
    style.textContent = css;
    document.head.appendChild(style);
  },

  /**
   * Create an element with attributes and children
   */
  createElement(tag, attrs = {}, ...children) {
    const el = document.createElement(tag);
    Object.entries(attrs).forEach(([k, v]) => {
      if (k === 'class') el.className = v;
      else if (k === 'style') Object.assign(el.style, v);
      else el.setAttribute(k, v);
    });
    children.forEach(child => {
      if (typeof child === 'string') el.appendChild(document.createTextNode(child));
      else if (child) el.appendChild(child);
    });
    return el;
  },
};

if (typeof window !== 'undefined') {
  window.DomUtil = DomUtil;
}