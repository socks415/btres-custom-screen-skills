(function(){
  // A minimal "settings" screen: a saved theme colour and name, shown units from the device settings.
  // Uses window.btScreen (never window.bT): btScreen.settings, btScreen.ready, btScreen.store.
  var root = document.getElementById('tb');
  if (!root || !window.btScreen) { if (root) root.textContent = 'This screen needs a newer bTres app (btScreen).'; return; }

  var store = btScreen.store(root);                 // storage for THIS screen (keyed by the screen's own id, not its position)
  var G = function(k){ var o = window.gaugeVars && gaugeVars[k]; if (!o || o.v === undefined || o.v === '') return null; var n = parseFloat(o.v); return isNaN(n) ? null : n; };
  var E = function(id){ return document.getElementById(id); };
  var HEX = /^#[0-9a-fA-F]{6}$/;
  var accent = '#7ee05a';

  function applyTheme(c, name){
    accent = c;
    E('tbTitle').style.color = c;
    E('tbBoost').style.color = c;
    E('tbTitle').textContent = (name || 'THEMED BOOST').toUpperCase();
  }
  function loadSaved(){
    var theme = store.get('theme', {accent: '#7ee05a', name: ''});    // default if nothing has been saved yet
    applyTheme(HEX.test(theme.accent) ? theme.accent : '#7ee05a', theme.name);
    E('tbHex').value = theme.accent; E('tbName').value = theme.name || '';
  }
  function save(c, name){
    if (store.set('theme', {accent: c, name: name})) { E('tbSaved').textContent = 'saved'; setTimeout(function(){ E('tbSaved').textContent = ''; }, 1500); }
  }

  [0,1,2,3].forEach(function(i){
    var sw = E('tbSw' + i);
    sw.addEventListener('click', function(){ var c = sw.getAttribute('data-c'); E('tbHex').value = c; applyTheme(c, E('tbName').value); save(c, E('tbName').value); });
  });
  // The on-screen keyboard sets the value and then triggers a *jQuery* 'change' event (not a native one): listen with $().on('change').
  $('#tbHex').on('change', function(){ var v = this.value.trim(); if (HEX.test(v)) { applyTheme(v, E('tbName').value); save(v, E('tbName').value); } });
  $('#tbName').on('change', function(){ applyTheme(accent, this.value); save(accent, this.value); });

  // Follow the device's own unit settings (see reference/units.md and units-snippet.js):
  //   mapBoost on  -> BOOST in psi (gauge, never below 0)     mapBoost off -> MAP in bar (absolute)
  //   ctoF on      -> Fahrenheit                              ctoF off     -> Celsius
  // Engine off (rpm < 300) the ECU reports a fixed 1013 hPa: treat that as ambient so boost reads 0.
  function boostValue(){
    var P = G('psrg_w'); if (P === null) P = G('psr_w'); if (P === null) return null;
    var A = G('pu_w'); if (A === null) A = 1013.25;
    var N = G('nmot_w'); if (N !== null && N < 300) P = A;
    return btScreen.settings.mapBoost ? Math.max(0, (P - A) * 0.0145037738) : P / 1000;
  }
  var bar = E('tbBar').getContext('2d');
  function tick(){
    var s = btScreen.settings;                                       // read-only copy of the device settings
    var boost = boostValue(), t = G('tmot');
    E('tbBoostLabel').textContent = s.mapBoost ? 'BOOST (psi)' : 'MAP (bar)';
    E('tbBoost').textContent = boost === null ? '--' : boost.toFixed(s.mapBoost ? 1 : 2);
    E('tbTemp').textContent = t === null ? '--' : (s.ctoF ? Math.round(t * 9 / 5 + 32) + ' \u00b0F' : Math.round(t) + ' \u00b0C');
    E('tbCar').textContent = [s.carModel, s.carWeight ? s.carWeight + ' lb' : ''].filter(Boolean).join('  \u00b7  ');
    var full = s.mapBoost ? 40 : 4;                                  // bar scale: 0..40 psi or 0..4 bar (absolute)
    bar.clearRect(0, 0, 1000, 40); bar.fillStyle = accent; bar.fillRect(0, 0, boost === null ? 0 : Math.max(0, Math.min(1000, boost / full * 1000)), 40);
  }

  btScreen.ready(function(){ loadSaved(); setInterval(tick, 100); });   // wait until settings and saved data have loaded
})();
