# GPS on bTres Pro units

**bTres Pro units** have a built-in GPS that updates **up to 20 times per second**. The bTres app keeps a GPS connection open the whole time it is running and lets custom screens listen to it. Your screen does not connect to anything: it **subscribes** to the app's existing GPS feed and gets a message for every update.

Other units have no GPS, so there is nothing to subscribe to. Check that the feed exists and show `--` (or a short "needs a bTres Pro" note) instead of throwing. The screen preview (`scripts/preview.py`) has no GPS either, so the empty state is what you will see there; feed fake messages yourself to test the live state (see the end).

## Subscribing

```js
function onGPS(event) {
  var d;
  try { d = JSON.parse(event.data); } catch (e) { return; }
  // d is one GPS message, see below
}
function onGPSClose() { /* the feed dropped; the app reconnects by itself within a few seconds */ }

if (typeof window._gpsSubscribe === 'function') {
  window._gpsSubscribe(onGPS, onGPSClose);   // onGPSClose is optional
}
// when your screen is torn down (optional but tidy):
// window._gpsUnsubscribe(onGPS, onGPSClose);
```

- Your handler receives the raw **event**: parse `event.data` yourself (it is a JSON string).
- **Messages arrive up to 20 times a second.** Don't touch the DOM on every message. Store the latest values in variables and draw from a `setInterval` (10 to 30 Hz), as in `patterns.md`. Anything done inside the handler must be cheap.
- **A handler that throws is silently removed** and never receives data again. Wrap the whole body in `try/catch`.
- Subscribing the same function twice does nothing.
- `window._gpsSubscribe` exists once the app has finished starting. If your code might run before that, start inside `btScreen.ready(function(){ ... })`, or retry on a short timer until it exists.
- Don't open your own connection to the GPS and don't use any other GPS global: `_gpsSubscribe` is the supported way.

## What each message contains

Every message is a JSON object. There are two kinds; tell them apart by which fields are present.

**Position message** (while the GPS has a fix, up to 20 per second):

| field | meaning |
|---|---|
| `status` | `"locked"` |
| `lat`, `lon` | position, decimal degrees |
| `speed_mph`, `speed_kmh`, `speed_knots` | ground speed from the GPS (not ECU or wheel speed) |
| `course` | heading in degrees (0 to 360, 0 = north, 90 = east); `null` when stationary |
| `altitude` | metres above sea level, or `null` |
| `sats` | number of satellites in use (a string, e.g. `"14"`) |
| `hdop` | accuracy figure (a string; lower is better, under 1.5 is good) |
| `timestamp` | time of the message (ISO text) |

**Status message** (no `lat` / `lon`): sent when the GPS state changes, and once when the app connects. `status` is one of:

- `"not_connected"`: no GPS hardware found.
- `"no_fix"`: GPS is working but has no satellite lock yet ("searching").
- `"error"`: a problem; there is an `error` text.

Don't update a speed or position readout from a status message: keep the last value or show `--`, and show the status if it helps ("Searching for satellites...").

Always check a field before using it: `if (d.lat !== undefined) {...}`, `if (typeof d.speed_mph === 'number') {...}`. Treat `sats` and `hdop` as strings (`parseFloat` them).

## Units

- **Follow the unit's settings.** Use `speed_mph` when `btScreen.settings.ctoF` is `true` and `speed_kmh` when it is `false` (same rule as `units.md`). Never hard-code "mph".
- A parked GPS can show 0.1 to 1 mph of drift. Treat speeds under about 1 mph as 0 for display.
- GPS speed is not wheel speed. Label it "GPS" when it sits next to other speed readouts.

## Stale data

Keep `lastMsg = Date.now()` in the handler. If nothing has arrived for more than about 1 second (`Date.now() - lastMsg > 1000`), the data is stale (lost signal, feed reconnecting): show `--` in the draw loop instead of the last number.

## Example: GPS speed readout

```js
var gps = {speed: null, lat: null, lon: null, sats: null, status: 'waiting', t: 0};

function onGPS(event) {
  try {
    var d = JSON.parse(event.data);
    gps.status = d.status || gps.status;
    gps.t = Date.now();
    if (d.lat !== undefined) {
      gps.lat = d.lat; gps.lon = d.lon; gps.sats = d.sats;
      var v = btScreen.settings.ctoF ? d.speed_mph : d.speed_kmh;
      gps.speed = (typeof v === 'number') ? (v < 1 ? 0 : v) : null;
    }
  } catch (e) {}
}

btScreen.ready(function () {
  if (typeof window._gpsSubscribe === 'function') {
    window._gpsSubscribe(onGPS, function () { gps.status = 'not_connected'; });
  }
  setInterval(function () {
    var fresh = Date.now() - gps.t < 1000 && gps.status === 'locked';
    T('gpsSpeed', fresh && gps.speed !== null ? Math.round(gps.speed) : '--');
    T('gpsUnit', btScreen.settings.ctoF ? 'mph' : 'km/h');
  }, 100);   // draw at 10 Hz, not on every message
});
```
(`T(id, text)` is the write-only-when-changed helper from `patterns.md`.)

## Testing without a unit

Call your handler with fake events of the same shape the app delivers:

```js
onGPS({data: JSON.stringify({status:'locked', lat:33.70, lon:-118.02, speed_mph:62.4, speed_kmh:100.4, speed_knots:54.2, course:270, altitude:12.3, sats:'14', hdop:'0.7'})});
onGPS({data: JSON.stringify({status:'no_fix'})});
```
Test: no data at all, `no_fix`, a fix at 0 mph, a fix at speed, and data stopping (stale). Say plainly in your handover that GPS behaviour was **not tested on a real bTres Pro unit** unless the user tells you it was.
