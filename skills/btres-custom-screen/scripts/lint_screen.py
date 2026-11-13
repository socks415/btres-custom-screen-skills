#!/usr/bin/env python3
"""Static lint for a bTres screen JSON: the mistakes that are easy to make and hard to see in a preview.

  python3 lint_screen.py screen.json [--unit s|m1x1]      lint a screen
  python3 lint_screen.py --selftest                       prove every check can fail

FAIL = fix it. WARN = read it and decide. Exit code 1 if any FAIL. This is static: it does not render the screen or
replay logs, and it never replaces testing on a real unit. (Adapted from a lint shared by Jim; reworked for the
btScreen API and the gallery scanner.)
"""
import base64, json, re, sys

LIMIT = 1048576
OPS = re.compile(r'[+\-*\\()]')
FOOTER_SAFE = {"s": 420, "m1x1": 620}      # content above this y stays clear of the 60 px footer when it is shown
HARD_UNITS = [(r'\bpsi\b', 'psi'), (r'°\s*F\b|&#176;F|&deg;F', 'degrees F'), (r'\bmph\b', 'mph'),
              (r'\bkm/h\b|\bkph\b', 'km/h'), (r'°\s*C\b|&#176;C|&deg;C', 'degrees C'), (r'\bbar\b', 'bar')]
PSI = r'14\.5037738|0\.0145037738|0\.145037738'
FAHR = r'9\s*/\s*5\s*\+\s*32|\*\s*1\.8\s*\+\s*32|1\.609344'
NET = [(r'\bfetch\s*\(', 'fetch()'), (r'\bXMLHttpRequest\b', 'XMLHttpRequest'), (r'\bWebSocket\b', 'WebSocket'),
       (r'\$\s*\.\s*(?:ajax|get|post|getJSON)\s*\(', 'jQuery ajax'), (r'\b(?:https?|wss?)://', 'a URL'),
       (r'\bnavigator\s*\.\s*sendBeacon\b', 'sendBeacon'), (r'\bimportScripts\b', 'importScripts')]


def extract_js(screen):
    """The JavaScript that a screen starts: eval("...") string literals and eval(atob('...')) payloads."""
    out = []
    texts = []
    for e in screen.get('elements', []):
        for k in ('monitor', 'text'):
            v = e.get(k)
            if isinstance(v, str):
                texts.append(v)
    for t in texts:
        t = t.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#x27;', "'")
        for m in re.finditer(r'eval\(\s*("(?:[^"\\]|\\.)*")\s*\)', t):
            try:
                out.append(json.loads(m.group(1)))
            except Exception:
                pass
        for m in re.finditer(r"eval\(\s*atob\(\s*'([A-Za-z0-9+/=]+)'\s*\)\s*\)", t):
            try:
                out.append(base64.b64decode(m.group(1)).decode('latin-1'))
            except Exception:
                pass
    return out


def lint(screen, size_bytes=None, unit=None):
    out = []
    add = lambda lvl, where, msg: out.append((lvl, where, msg))
    if not isinstance(screen, dict) or 'elements' not in screen or 'settings' not in screen:
        return [('FAIL', 'screen', 'not {"settings": {...}, "elements": [...]}')]
    els = screen['elements']
    if not els:
        add('FAIL', 'screen', 'no elements')
    if size_bytes is not None and size_bytes >= LIMIT:
        add('FAIL', 'screen', 'file is %.2f MB: the gallery limit for a screen JSON is 1.00 MB' % (size_bytes / LIMIT))
    footer_on = bool(screen['settings'].get('showFooterBar'))
    safe = FOOTER_SAFE.get(unit, FOOTER_SAFE['s'])
    js_all = extract_js(screen)
    js = '\n'.join(js_all)

    for i, e in enumerate(els):
        t = e.get('type')
        where = 'element %d (%s)' % (i, t)
        for k in ('x', 'y', 'width', 'height'):
            v = e.get(k)
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                add('FAIL', where, '%s=%r is not a number: the unit ignores string geometry and the element draws at 0,0' % (k, v))
        try:
            if footer_on and e['y'] + e['height'] > safe and e['width'] > 10 and e['height'] > 10:
                add('WARN', where, 'bottom edge %d is under the footer (y > %d) and showFooterBar is on: set it to false or move content up' % (e['y'] + e['height'], safe))
        except Exception:
            pass
        if t in ('textData', 'radialNeedle', 'meter'):
            m = e.get('monitor') or ''
            if m and 'eval(' not in m:                       # a native monitor (formula), not a script starter
                if not OPS.search(m):
                    add('WARN', where, 'monitor has none of + - * \\ ( ): the unit shows it as text and never evaluates it; wrap it in parentheses')
                if e.get('minMax') in ('min', 'max') and '​' in m:
                    add('FAIL', where, 'min/max element returns a string (ends in U+200B): min/max becomes NaN')
                raw = sorted(set(re.findall(r'(?<![\w\])\]])\[([A-Za-z_][A-Za-z0-9_]*)\]', m)))
                if raw:
                    add('WARN', where, 'raw [var] in a formula breaks it if the car does not send the column: ' + ', '.join(raw))
                if re.search(PSI, m) and 'calcBoost' not in m:
                    add('FAIL', where, 'converts to psi without reading calcBoost: ignores the unit setting')
                if re.search(FAHR, m) and 'switchF' not in m:
                    add('FAIL', where, 'converts to F or mph without reading switchF: ignores the unit setting')
            pre = ' '.join(str(e.get(k, '')) for k in ('preText', 'postText'))
            if m and 'eval(' not in m:
                for rx, name in HARD_UNITS:
                    if re.search(rx, pre, re.I) and not ('calcBoost' in m or 'switchF' in m):
                        add('WARN', where, 'hard-coded unit "%s" in pre/postText: it will be wrong when the unit setting changes' % name)
            if e.get('preText') is None or e.get('postText') is None:
                add('WARN', where, 'preText/postText missing: the unit prints "undefined" (use empty strings)')
        elif t == 'text':
            txt = re.sub(r'<style.*?</style>|<script.*?</script>|<[^>]+>', ' ', e.get('text') or '', flags=re.S)
            for rx, name in HARD_UNITS:
                if re.search(rx, txt, re.I):
                    add('WARN', where, 'static text shows the unit "%s": make it follow btScreen.settings (mapBoost / ctoF) or document that the screen is one unit system' % name)

    if js:
        code = re.sub(r'/\*.*?\*/', '', js, flags=re.S)
        code = re.sub(r'(?<![:\w"\'])//[^\n]*', '', code)     # comments don't count (rough: a // inside a string is also dropped)
        for rx, name in NET:
            if re.search(rx, js):
                add('FAIL', 'script', 'uses %s: screens must not reach outside the device, and the gallery scanner flags it' % name)
        if re.search(r'\bwindow\s*\.\s*bT\b|(?<![\w.])bT\s*\.', code):
            add('WARN', 'script', 'reads window.bT: use window.btScreen (settings, store, ready) instead; bT holds internals that must not be touched')
        if re.search(r'\blocalStorage\b|\bsessionStorage\b|\bindexedDB\b', code):
            add('WARN', 'script', 'uses browser storage (localStorage / sessionStorage / IndexedDB): it is NOT persistent on the unit and is lost on restart. Use btScreen.store() for saved data')
        if re.search(PSI, code) and not re.search(r'mapBoost|calcBoost', code):
            add('WARN', 'script', 'converts to psi without checking btScreen.settings.mapBoost: the unit may be set to show MAP in bar')
        if re.search(FAHR, code) and not re.search(r'ctoF|switchF', code):
            add('WARN', 'script', 'converts C to F / km/h to mph without checking btScreen.settings.ctoF: the unit may be set to Celsius')
        if re.search(r"addEventListener\(\s*['\"](?:change|input)['\"]", code) and re.search(r'<input', json.dumps(screen)):
            add('WARN', 'script', "listens for a native change/input event on an <input>: the on-screen keyboard only triggers jQuery's change event, use $(el).on('change', ...) (see reference/app-api.md)")
        if re.search(r'\bbtScreen\b', code) and not re.search(r'window\.btScreen|typeof btScreen|!btScreen|btScreen\s*&&|btScreen\s*\)|btScreen\s*===?\s*undefined', code):
            add('WARN', 'script', 'uses btScreen without checking it exists: older app versions do not have it')
        if re.search(r'screen_\d+|element_\d+_\d+', code):
            add('WARN', 'script', 'refers to screen_N / element_N_M ids: those are positions and change; find your elements by your own unique ids')
        if re.search(r'requestAnimationFrame|setInterval', code) is None and re.search(r'gaugeVars', code):
            add('WARN', 'script', 'reads gaugeVars but never repeats (no setInterval / requestAnimationFrame): values will not update')
    return out


def report(out):
    for lvl, where, msg in out:
        print('%s %s: %s' % (lvl, where, msg))
    fails = sum(1 for o in out if o[0] == 'FAIL')
    print('SUMMARY %d FAIL, %d WARN (static lint only: no render, no log replay, not a unit test)' % (fails, sum(1 for o in out if o[0] == 'WARN')))
    return fails


def selftest():
    bad = 0

    def mk(js='', html='', **kw):
        code = ('(window.k||(window.k=1,eval(%s)))' % json.dumps(js)) if js else ''
        els = [dict({'type': 'text', 'text': html, 'x': 0, 'y': 0, 'width': 1920, 'height': 480}, **kw)]
        if code:
            els.append({'type': 'textData', 'monitor': code, 'preText': '', 'postText': '', 'x': 0, 'y': 0, 'width': 10, 'height': 35})
        return {'settings': {'showFooterBar': False}, 'elements': els}
    good = mk('setInterval(function(){var s=window.btScreen&&btScreen.settings;},100)', '<div>hi</div>')
    f = [o for o in lint(good) if o[0] == 'FAIL']
    print(('PASS' if not f else 'FAIL') + ' clean screen has no FAIL ' + str(f)); bad += bool(f)
    cases = [
        ('string geometry', mk(html='x', x='14'), 'FAIL', 'not a number'),
        ('network call', mk("fetch('/x'); setInterval(1,1)"), 'FAIL', 'fetch()'),
        ('url', mk("var u='https://example.com'; setInterval(1,1)"), 'FAIL', 'a URL'),
        ('window.bT', mk('var c=window.bT.carModel; setInterval(1,1)'), 'WARN', 'window.bT'),
        ('localStorage', mk("localStorage.setItem('a',1); setInterval(1,1)"), 'WARN', 'browser storage'),
        ('psi without mapBoost', mk('var p=x*0.0145037738; setInterval(1,1)'), 'WARN', 'mapBoost'),
        ('F without ctoF', mk('var f=c*9/5+32; setInterval(1,1)'), 'WARN', 'ctoF'),
        ('hard-coded psi text', mk(html='<b>BOOST psi</b>'), 'WARN', 'static text'),
        ('native keyboard listener', mk("document.getElementById('a').addEventListener('change',f); setInterval(1,1)", '<input id="a">'), 'WARN', 'jQuery'),
        ('btScreen unchecked', mk('var s=btScreen.store(x); setInterval(1,1)'), 'WARN', 'older app'),
        ('position ids', mk("document.getElementById('screen_1'); setInterval(1,1)"), 'WARN', 'positions'),
        ('never repeats', mk('var v=gaugeVars.a'), 'WARN', 'never repeats'),
    ]
    for name, scr, lvl, sub in cases:
        hit = [o for o in lint(scr) if o[0] == lvl and sub in o[2]]
        print(('PASS' if hit else 'FAIL') + ' CONTROL %s is caught' % name); bad += not hit
    big = [o for o in lint(good, size_bytes=LIMIT + 1) if 'limit' in o[2]]
    print(('PASS' if big else 'FAIL') + ' CONTROL over 1 MB is caught'); bad += not big
    low = {'settings': {'showFooterBar': True}, 'elements': [{'type': 'text', 'text': 'x', 'x': 1, 'y': 580, 'width': 50, 'height': 30}]}
    a, b = [o for o in lint(low, unit='s') if 'footer' in o[2]], [o for o in lint(low, unit='m1x1') if 'footer' in o[2]]
    print(('PASS' if a and not b else 'FAIL') + ' CONTROL footer limit depends on the unit'); bad += not (a and not b)
    nm = {'settings': {}, 'elements': [{'type': 'textData', 'monitor': '([x]*0.0145037738)', 'preText': '', 'postText': '', 'x': 1, 'y': 1, 'width': 5, 'height': 5}]}
    hit = [o for o in lint(nm) if 'calcBoost' in o[2]]
    print(('PASS' if hit else 'FAIL') + ' CONTROL native psi formula without calcBoost is caught'); bad += not hit
    print('ALL PASS' if not bad else 'FAILED %d' % bad)
    return 1 if bad else 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    if sys.argv[1] == '--selftest':
        sys.exit(selftest())
    unit = sys.argv[sys.argv.index('--unit') + 1] if '--unit' in sys.argv else None
    data = open(sys.argv[1], 'rb').read()
    sys.exit(1 if report(lint(json.loads(data), len(data), unit)) else 0)
