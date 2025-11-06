(function(){
  async function ask() {
    var elQ = document.getElementById('q');
    var elOut = document.getElementById('out');
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