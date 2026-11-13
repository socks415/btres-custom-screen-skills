# The bTres screen API: `window.btScreen`

Custom screens talk to the bTres app through **`window.btScreen`**. **Never use `window.bT`**: it holds the app's internals and must not be read or changed by screens (what screens may use is exposed here, on purpose). `btScreen` gives screens three things: a read-only copy of the device settings they may use, saved data that survives restarts, and a way to run code once everything has loaded. The on-screen keyboard works on its own (see the end).

`btScreen` exists only in app versions that include it. A screen that needs it should check `window.btScreen` first and show a short message ("needs a newer bTres app") or fall back, instead of throwing. `btScreen.version` is `1`.

## `btScreen.settings` (read-only)
A frozen snapshot of the device settings screens can use. `settings.loaded` is `true` once the app has fetched them; use `btScreen.ready()` to wait. Everything here is a copy: changing it does nothing.

| field | type | meaning |
|---|---|---|
| `ctoF` | boolean | `true`: the user wants temperatures in Fahrenheit, and speeds in mph (device setting "Switch C to F"). DS1 temperatures are always Celsius; convert for display, see `units.md` |
| `mapBoost` | boolean | `true`: show **BOOST in psi** (gauge, above ambient); `false`: show **MAP in bar**, absolute ("Swap Map to Boost"). Screens should follow it, see `units.md` |
| `ds1Url` | string | address of the DS1 dongle (default `ds1.local`) |
| `map1` ... `map9` | string | the names the user gave ECU maps **0 to 8**: `map1` is map 0, `map9` is map 8 (match with `gaugeVars.mapswitch`). Empty if unnamed |
| `launchBoost` | number or `null` | launch boost target in **bar of MAP**; `null` means launch boost is off |
| `carModel` | string | the car chosen in settings, e.g. `S8`, `RS3`, `TTRS`, `R8` |
| `carWeight` | number or `null` | pounds |
| `tireWidth` | number or `null` | millimetres |
| `tireRatio` | number or `null` | aspect ratio, % |
| `tireRim` | number or `null` | rim diameter, inches |

Only these fields are exposed. Passwords, the lockout PIN, Wi-Fi details and the rest of the config are never visible to screens.

```js
var s = btScreen.settings;
var coolant = s.ctoF ? Math.round(c * 9 / 5 + 32) + ' °F' : Math.round(c) + ' °C';
```
The settings can change while the screen is up (the app re-reads them): the `document` event `btsettings` fires each time they are (re)loaded, and `btScreen.settings` always returns the latest snapshot.

## `btScreen.ready(fn)`
Runs `fn` once the settings **and** the saved data have loaded (or right away if they already have). Start your screen inside `ready`, so the first thing drawn already uses the saved theme and the right units.

## `btScreen.store(el)`: saved data for this screen
```js
var store = btScreen.store(document.getElementById('myRoot'));   // any element inside your screen
store.get('theme', {accent: '#7ee05a'});    // read; the default is returned if nothing is saved
store.set('theme', {accent: '#ff0000'});    // write (any JSON); returns true, or false if rejected
store.remove('theme');  store.clear();  store.all();
store.available;                            // false if this screen has no id yet (see below)
```
- **Which screen's data?** The app finds the screen that contains the element you pass and uses that screen's stable id. It is **not** `screen_1`, `screen_2`, ... (those are positions and change when screens are reordered). Two screens never share or overwrite each other's data.
- **Reads are instant** (everything is loaded before screens start), writes are saved a moment later (batched, so changing a slider doesn't wear the SD card). Don't call `set` 60 times a second; call it when the user changes something.
- **Values**: anything that survives `JSON.stringify` (objects, arrays, strings, numbers, booleans, `null`). `get` returns a copy, so change a copy and `set` it back.
- **Limits**: up to **100 KB** of saved data per screen (as JSON), up to 200 keys, key names `A-Z a-z 0-9 _ . -` (max 64 characters). A `set` that would break a limit returns `false`, logs a warning, and changes nothing.
- **When data is kept or deleted**: it survives restarts, power loss and **screen updates** (installing a newer version of the same screen from the gallery keeps its data). Uninstalling or removing the screen deletes it. Reinstalling a screen that was uninstalled starts fresh.
- **Hand-uploaded screens** get an id when they are saved on the device; before that `store.available` is `false` and values don't persist.
- **Version your data**: if a later version of your screen changes what it saves, store a `version` number with it and migrate old data on load, because users keep their saved data across your updates.
- **Not for secrets.** All screens run in the same page: this prevents accidents (collisions, one screen's bug overwriting another's data) but is not a security boundary. Don't store anything private.
- **Browser storage is not persistent on the unit.** `localStorage`, `sessionStorage` and IndexedDB are not kept: the kiosk browser is run so that it persists nothing, so anything written there is lost on restart (it may appear to work until then). `btScreen.store()` is the only way to keep data.

Typical pattern:
```js
btScreen.ready(function(){
  var theme = store.get('theme', defaultTheme);   // load
  apply(theme);
  onUserChanges(function(t){ apply(t); store.set('theme', t); });   // save when the user changes it
});
```
`examples/themed-boost/` is a complete screen using settings, storage and the keyboard.

## The on-screen keyboard
The bTres app has its **own virtual (on-screen) keyboard**. It is not a browser or system keyboard: the kiosk browser on the unit has none, so this is the only keyboard available there. It opens by itself when the user taps a text field in your screen; there is nothing to call or load.
- Add a normal field: `<input type="text">`, `password`, `email` (full keyboard) or `type="number"`, `type="tel"`, or any input with `class="number"` (numeric keypad: digits, `.`, `-`, Backspace, Clear, Cancel, Enter).
- Give the input **`pointer-events:all`**: screen elements ignore touches by default.
- **Listen with jQuery.** The keyboard puts each character into `input.value` and then triggers a **jQuery** `change` event (on every key press). It does **not** fire native `input` or `change` events, so `addEventListener('change', ...)` never runs on the unit. Use `$('#myInput').on('change', fn)` (jQuery is always on the page). Don't also attach a native listener for the same event: on a phone or desktop browser, jQuery handlers *do* run for native events and you would handle it twice.
- **Enter** and **Cancel** close the keyboard (Cancel restores the field's previous value). Read the value in your `change` handler; there is no "closed" event, so save on `change` (the store batches writes).
- The virtual keyboard only appears on the unit itself. If the same screen is opened in an ordinary browser (a phone or computer), that device's own keyboard is used instead, so the field works the same way there.
- The keyboard is large (about 1200 x 370 px at the S-series size) and covers part of the screen while open. Leave room, or put inputs where covering the rest of the screen is fine. On M1 / X1 the keyboard is placed next to the field and is nearly as wide as the screen.
- Limit what users can type (`maxlength`, validate in your `change` handler: for example accept `#rrggbb` only) and keep a sensible default when the input is invalid.

## Building and previewing with the mock
`scripts/preview.py` provides a stand-in `btScreen` (same API and limits, in memory only) so you can see the screen before it is on a unit. `--settings '{"ctoF":true,"carModel":"RS3"}'` overrides the settings and `--data '{"theme":{...}}'` seeds the saved data (to preview "after the user saved a theme"). Preview can't open the on-screen keyboard; test inputs on a real unit.

## Don't
- Don't touch `window.bT` or call the app's endpoints; the gallery scanner flags `fetch` / `XMLHttpRequest` / `WebSocket` and any other outside access.
- Don't assume `btScreen` or any setting exists: handle `null` / empty values (a unit may have no car weight set).
- Don't rely on `screen_N` ids or element order to identify a screen.
