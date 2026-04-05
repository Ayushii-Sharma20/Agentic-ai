// highlighter.js — standalone highlight utilities (loaded before content.js)

window.TCHighlighter = {
  /**
   * Wrap all occurrences of `text` in a <mark> with given class.
   */
  highlight(text, className) {
    if (!text || text.length < 10) return;
    const escaped = text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(escaped.slice(0, 60), 'gi');

    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const matches = [];
    let node;

    while ((node = walker.nextNode())) {
      if (['SCRIPT', 'STYLE'].includes(node.parentElement?.tagName)) continue;
      if (regex.test(node.textContent)) {
        matches.push(node);
      }
    }

    matches.forEach(n => {
      const mark = document.createElement('mark');
      mark.className = className;
      try {
        n.parentNode.insertBefore(mark, n);
        mark.appendChild(n);
      } catch {
        // ignore
      }
    });
  },

  /**
   * Remove all highlights with the given class.
   */
  clearClass(className) {
    document.querySelectorAll(`.${className}`).forEach(el => {
      const parent = el.parentNode;
      while (el.firstChild) parent.insertBefore(el.firstChild, el);
      parent.removeChild(el);
    });
  },

  /**
   * Scroll to first highlight.
   */
  scrollToFirst(className) {
    const first = document.querySelector(`.${className}`);
    if (first) {
      first.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  },
};