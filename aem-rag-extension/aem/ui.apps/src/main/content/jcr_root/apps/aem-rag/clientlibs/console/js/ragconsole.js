(function() {
  async function submitRagQuery() {
    const elQ = document.getElementById('rag-query');
    const resultsDiv = document.getElementById('rag-results');
    const query = elQ.value.trim();
    if (!query) return;
    resultsDiv.innerHTML = '<p>🔎 Querying AEM RAG index...</p>';
    try {
      const res = await fetch('/bin/ragquery', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query: query})
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      function renderObject(obj) {
        return Object.entries(obj).map(([key, value]) => {
          if (value && typeof value === 'object') {
            return `<div class="field"><span class="label">${key}</span>${renderObject(value)}</div>`;
          } else {
            return `<div class="field"><span class="label">${key}</span>${value ?? 'n/a'}</div>`;
          }
        }).join('');
      }
      resultsDiv.innerHTML = `<h3>🧠 Response</h3>${renderObject(data)}`;
    } catch (err) {
      resultsDiv.innerHTML = `<p style="color:#ff6b6b">❌ ${err.message}</p>`;
    }
  }
  window.submitRagQuery = submitRagQuery;
})();
  async function ask() {
    var elQ = document.getElementById('rag-query');
    var elOut = document.getElementById('rag-results');
    var q = elQ.value || '';
    if(!q.trim()){ elOut.textContent = 'Please enter a question.'; return; }
    elOut.textContent = 'Querying...';
    try {
      const res = await fetch('/bin/ragquery', {
        method:'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({question:q})
      });
      const json = await res.json();
      elOut.innerText = json.answer || '(no answer)';
    } catch(e) {
      elOut.textContent = 'Error: ' + e;
    }
  }
  window.ask = ask;
})();