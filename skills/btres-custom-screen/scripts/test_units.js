// Self-test for reference/units-snippet.js. Run with jsc (macOS: /System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc),
// node, or any JS shell:   node scripts/test_units.js
// The expected values are worked out by hand, and the CONTROLs (wrong formulas) must fail, otherwise a check proves nothing.
var fs = (typeof require !== 'undefined') ? require('fs') : null;
var load = function(path){ return fs ? fs.readFileSync(path, 'utf8') : readFile(path); };
var here = (typeof __dirname !== 'undefined') ? __dirname : '.';
var src = load(here + '/../reference/units-snippet.js');
var out = (typeof console !== 'undefined') ? console.log : print;
var fail = 0;
function mk(vars, mapBoost, ctoF){
  var w = { gaugeVars: {}, btScreen: { settings: { mapBoost: mapBoost, ctoF: ctoF } } };
  for (var k in vars) w.gaugeVars[k] = { v: vars[k] };
  (new Function('window', 'return (function(){ ' + src + ' }).call(window)'))(w);   // runs the snippet with window = w
  return w.btUnits;
}
function near(a, b, t){ return a !== null && Math.abs(a - b) <= (t || 0.005); }
function chk(name, ok, seen){ if (!ok) fail++; out((ok ? 'PASS ' : 'FAIL ') + name + '  ' + seen); }
var pull = { psrg_w: 2900, psrs_w: 3000, pu_w: 971, nmot_w: 5500, toel: 100, pbkist_w: 1000 };
var idle = { psrg_w: 300, psrs_w: 300, pu_w: 971, nmot_w: 750 };
var off  = { psrg_w: 1013, pu_w: 971, nmot_w: 0 };
[true, false].forEach(function(mb){ [true, false].forEach(function(cf){
  var m = 'mapBoost=' + mb + ' ctoF=' + cf + ' ';
  var u = mk(pull, mb, cf), ui = mk(idle, mb, cf), uo = mk(off, mb, cf);
  chk(m + 'boost pull',   near(u.boost(), mb ? 27.98 : 2.9), u.boost());
  chk(m + 'target pull',  near(u.target(), mb ? 29.43 : 3.0), u.target());
  chk(m + 'boost idle',   near(ui.boost(), mb ? 0 : 0.3), ui.boost());
  chk(m + 'engine off',   near(uo.boost(), mb ? 0 : 0.971), uo.boost());
  chk(m + 'oil temp',     near(u.temp('toel'), cf ? 212 : 100, 0.01), u.temp('toel'));
  chk(m + 'lpfp 1000 kPa', near(u.kpa('pbkist_w'), mb ? 145.04 : 10, 0.01), u.kpa('pbkist_w'));
  chk(m + 'labels', u.labels.pressure() === (mb ? 'psi' : 'bar') && u.labels.temp() === (cf ? '°F' : '°C') && u.labels.speed() === (cf ? 'mph' : 'km/h'), '');
  chk(m + 'axis max', u.pressureMax(30) === (mb ? 30 : 3), u.pressureMax(30));
  chk(m + '100 km/h', near(mk({ v: 100 }, mb, cf).speed('v'), cf ? 62.137 : 100, 0.01), mk({ v: 100 }, mb, cf).speed('v'));
}); });
chk('missing column -> null (not 0)', mk({}, true, true).boost() === null && mk({}, true, true).temp('toel') === null, '');
chk('fallback psr_w, no pu_w, no rpm', near(mk({ psr_w: 2013.25 }, true, true).boost(), 14.5, 0.01), mk({ psr_w: 2013.25 }, true, true).boost());
// CONTROLS: these wrong formulas must be caught by the numbers above.
chk('CONTROL gauge-bar bug is caught', !near((2900 - 971) / 1000, 2.9), (2900 - 971) / 1000 + ' (must differ from 2.9)');
chk('CONTROL unfloored vacuum is caught', !near((300 - 971) * 0.0145037738, 0), (300 - 971) * 0.0145037738 + ' (must not be 0)');
out(fail ? 'FAILED ' + fail : 'ALL PASS');
if (typeof process !== 'undefined') process.exit(fail ? 1 : 0);
