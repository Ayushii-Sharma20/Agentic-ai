// utils/storage.js — Chrome storage wrapper

const StorageUtil = {
  /**
   * Save analysis result
   */
  async save(entry) {
    const { recentAnalyses = [] } = await chrome.storage.local.get('recentAnalyses');
    const filtered = recentAnalyses.filter(r => r.url !== entry.url);
    const updated = [entry, ...filtered].slice(0, 30);
    await chrome.storage.local.set({ recentAnalyses: updated });
  },

  /**
   * Get all recent analyses
   */
  async getRecent() {
    const { recentAnalyses = [] } = await chrome.storage.local.get('recentAnalyses');
    return recentAnalyses;
  },

  /**
   * Get analysis by URL
   */
  async getByUrl(url) {
    const recent = await this.getRecent();
    return recent.find(r => r.url === url) || null;
  },

  /**
   * Clear all stored analyses
   */
  async clearAll() {
    await chrome.storage.local.remove('recentAnalyses');
  },

  /**
   * Get/set user preferences
   */
  async getPrefs() {
    const { prefs = {} } = await chrome.storage.local.get('prefs');
    return {
      autoAnalyze: false,
      showBanner: true,
      highlightClauses: true,
      apiUrl: 'http://localhost:8000',
      ...prefs,
    };
  },

  async savePrefs(prefs) {
    const current = await this.getPrefs();
    await chrome.storage.local.set({ prefs: { ...current, ...prefs } });
  },
};

if (typeof window !== 'undefined') {
  window.StorageUtil = StorageUtil;
}