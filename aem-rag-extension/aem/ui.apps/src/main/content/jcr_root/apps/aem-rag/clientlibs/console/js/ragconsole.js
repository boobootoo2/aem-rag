(function() {
  /**
   * AEM RAG Console - Client Library
   * Provides functions for querying the RAG servlet at /bin/aemrag/query
   */

  /**
   * Load cache statistics and update the UI
   */
  async function loadCacheStats() {
    try {
      const res = await fetch('/bin/aemrag/query?query=_stats', {
        credentials: 'same-origin'
      });
      const stats = await res.json();
      const cacheSize = document.getElementById('cacheSize');
      const hitRate = document.getElementById('hitRate');
      const totalRequests = document.getElementById('totalRequests');
      
      if (cacheSize) cacheSize.textContent = stats.cacheSize + ' / ' + stats.maxCacheSize;
      if (hitRate) hitRate.textContent = stats.hitRate;
      if (totalRequests) totalRequests.textContent = stats.totalRequests;
      
      return stats;
    } catch (err) {
      console.error('Failed to load cache stats:', err);
      return null;
    }
  }

  /**
   * Clear the query cache
   */
  async function clearCache() {
    if (!confirm('Clear all cached queries?')) return false;
    
    try {
      await fetch('/bin/aemrag/query?query=_clear', {
        credentials: 'same-origin'
      });
      alert('Cache cleared successfully');
      loadCacheStats();
      return true;
    } catch (err) {
      alert('Failed to clear cache: ' + err.message);
      return false;
    }
  }

  /**
   * Submit a RAG query and display results
   */
  async function submitQuery(e) {
    if (e) e.preventDefault();
    
    const prompt = document.getElementById('userInput').value.trim();
    const responseDiv = document.getElementById('response');
    
    if (!prompt) {
      responseDiv.innerHTML = '<div class="error">❌ Please enter a question</div>';
      return;
    }

    responseDiv.innerHTML = '<div class="loading">🔎 Querying AEM RAG index...</div>';

    const startTime = Date.now();
    try {
      const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';
      const headers = { 
        'Content-Type': 'application/json'
      };
      if (csrfToken) {
        headers['CSRF-Token'] = csrfToken;
      }
      
      const res = await fetch('/bin/aemrag/query', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ query: prompt }),
        credentials: 'same-origin'
      });
      
      const duration = Date.now() - startTime;
      const data = await res.json();
      
      if (data.error) throw new Error(data.error);

      var html = '<div class="response-section">';
      
      html += '<h3>🧠 Answer';
      if (data.cached !== undefined) {
        var cacheClass = data.cached ? 'cache-hit' : 'cache-miss';
        var cacheText = data.cached ? '✓ CACHED' : '⚡ FRESH';
        html += '<span class="cache-badge ' + cacheClass + '">' + cacheText + '</span>';
      }
      html += '</h3>';
      
      html += '<div class="answer-box">' + (data.answer || 'No answer provided') + '</div>';
      
      if (data.sources && data.sources.length > 0) {
        html += '<div class="sources-section">';
        html += '<h4>📚 Sources (' + data.sources.length + ')</h4>';
        data.sources.forEach(function(source, idx) {
          html += '<div class="source-item">';
          html += '<div class="source-path">' + (idx + 1) + '. ' + source.path + '</div>';
          html += '<div class="source-excerpt">' + source.excerpt + '</div>';
          html += '</div>';
        });
        html += '</div>';
      }
      
      html += '<div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e0e0e0; font-size: 12px; color: #666;">';
      html += 'Response time: ' + duration + 'ms';
      if (data.cacheAge) {
        html += ' | Cache age: ' + Math.round(data.cacheAge / 1000) + 's';
      }
      html += '</div>';
      
      html += '</div>';
      
      responseDiv.innerHTML = html;
      
      loadCacheStats();
      
    } catch (err) {
      responseDiv.innerHTML = '<div class="error">❌ Error: ' + err.message + '</div>';
    }
  }

  /**
   * Initialize the console when DOM is ready
   */
  function initConsole() {
    loadCacheStats();
    
    const queryForm = document.getElementById('queryForm');
    if (queryForm) {
      queryForm.addEventListener('submit', submitQuery);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initConsole);
  } else {
    initConsole();
  }

  // Export functions to global scope
  window.loadCacheStats = loadCacheStats;
  window.clearCache = clearCache;
  window.submitQuery = submitQuery;
})();