// utils/api.js — API communication layer

const API_BASE = 'http://localhost:8000/api/v2';

const ApiUtil = {
  /**
   * Analyze text via backend pipeline
   * @param {string} text
   * @param {string} [url]
   * @returns {Promise<Object>}
   */
  async analyze(text, url = '') {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, url }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Request failed with status ${res.status}`);
    }

    return res.json();
  },

  /**
   * Check API health
   * @returns {Promise<{status: string, version: string, agents_loaded: boolean}>}
   */
  async health() {
    const res = await fetch(`${API_BASE}/health`, {
      signal: AbortSignal.timeout(4000),
    });
    if (!res.ok) throw new Error('API unhealthy');
    return res.json();
  },
};

// Make globally available in extension context
if (typeof window !== 'undefined') {
  window.ApiUtil = ApiUtil;
}