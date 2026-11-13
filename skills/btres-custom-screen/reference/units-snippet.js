// Unit-aware helpers for bTres screens (copy what you need into screen.js).
// They follow the device's two unit settings through btScreen.settings:
//   mapBoost true  -> show BOOST in psi, gauge (above ambient), never below 0     false -> show MAP in bar, ABSOLUTE
//   ctoF     true  -> Fahrenheit (and mph; the unit has no separate speed setting)  false -> Celsius (km/h)
// Everything internal stays metric (hPa, kPa, deg C, km/h); convert only when displaying.
// Every function returns null when a needed value is missing: show '--' for null, never 0.
(function(root){
  var G = function(k){ var o = root.gaugeVars && root.gaugeVars[k]; if (!o || o.v === undefined || o.v === '') return null; var n = parseFloat(o.v); return isNaN(n) ? null : n; };
  var S = function(){ return (root.btScreen && root.btScreen.settings) || {}; };

  // Absolute pressure in hPa from the first column that has a value (boost and target differ per car, see reference/variables.md).
  function absHpa(cols){ for (var i = 0; i < cols.length; i++) { var v = G(cols[i]); if (v !== null) return v; } return null; }

  // Ambient pressure: pu_w is only logged about 1 row in 9 (the unit holds the last value); 1013.25 until it has arrived.
  function ambient(){ var a = G('pu_w'); return a === null ? 1013.25 : a; }

  // Boost-style pressure for display. mapBoost: psi gauge >= 0. otherwise: absolute MAP in bar (about 0.3 idle, 1.0 off, about 3.0 at 29 psi).
  // Engine off (rpm < 300): the ECU reports a fixed 1013 hPa, so treat it as ambient (zero boost). Skipped if the car sends no rpm.
  function pressure(cols){
    var P = absHpa(cols); if (P === null) return null;
    var A = ambient(), N = G('nmot_w'); if (N !== null && N < 300) P = A;
    return S().mapBoost ? Math.max(0, (P - A) * 0.0145037738) : P / 1000;
  }
  var boost  = function(){ return pressure(['psrg_w', 'psr_w']); };
  var target = function(){ return pressure(['psrs_w', 'pvds_w']); };   // psrs_w first (the V8 lists have it; the RS3 list only has pvds_w)

  var labels = {
    pressure: function(){ return S().mapBoost ? 'psi' : 'bar'; },
    boostName: function(){ return S().mapBoost ? 'BOOST' : 'MAP'; },
    temp: function(){ return S().ctoF ? '°F' : '°C'; },
    speed: function(){ return S().ctoF ? 'mph' : 'km/h'; }
  };
  // Axis maximum that suits the unit: a boost bar running 0..30 in psi mode must run 0..3 in bar mode.
  var pressureMax = function(psiMax){ return S().mapBoost ? psiMax : psiMax / 10; };

  var temp  = function(col){ var v = G(col); return v === null ? null : (S().ctoF ? v * 9 / 5 + 32 : v); };            // any Celsius column
  var speed = function(col){ var v = G(col); return v === null ? null : (S().ctoF ? v / 1.609344 : v); };              // any km/h value
  var kpa   = function(col){ var v = G(col); return v === null ? null : (S().mapBoost ? v * 0.145037738 : v / 100); };  // kPa pressures (check gauge vs absolute first)

  root.btUnits = { G: G, boost: boost, target: target, temp: temp, speed: speed, kpa: kpa, labels: labels, pressureMax: pressureMax, pressure: pressure };
})(typeof window !== 'undefined' ? window : this);
