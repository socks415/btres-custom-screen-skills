# DS1 variables

Every DS1 monitor, default or custom, shows up in `window.gaugeVars` under its variable name: `gaugeVars["nmot_w"].v`. A variable only exists if the user's DS1 setup logs it; always handle missing values.

## The full monitor lists (use these, don't guess)
The complete out-of-the-box (OTS) monitor lists for the supported cars are bundled in `ds1-monitors/`:

| car | file | entries |
|---|---|---|
| 6 / 7 / 8 series Audi (V8, MED17.1.1) | `ds1-monitors/6-7-8-series.json` | 354 |
| RS3 / TT RS (2.5 TFSI) | `ds1-monitors/rs3-ttrs.json` | 347 |

Each entry: `var` (the name used in `gaugeVars`), `desc` (DS1's description), `unit` (the metric unit), `scale` and `offset` (the DS1 conversion of the raw ECU value). Search them with `python3 scripts/find_monitor.py --car v8|rs3 <keywords>` and verify names with `--exact name1 name2 ...`. A name that is not found for the user's car must not be used: ask the user.

**How to read a monitor's name** (from the DS1 lists): the variable is the value between the first parentheses of the DS1 label, e.g. `Eng spd(nmot_w)(1/min)` is `nmot_w` in 1/min. Generally the `act` / plain one is the real measured value and `tgt` / `target` is the target (e.g. `HPF act unfilt B1(prroh_w)` vs `HPF tgt B1(prsoll_w)`; `Lambda act` vs `Lambda tgt`). Bank 1 / bank 2 appear as `B1` / `B2` and a `2` in the name on the V8.

**Units**: values in `gaugeVars` are in the metric unit the list shows (hPa, kPa, MPa, deg C, ...), already converted by DS1. Convert on the screen for display (psi, F). For other cars than the two lists, ask the user for their monitor list (the DS1 variable list / metric-units export) and use the same lookup approach.

**Density altitude** is not read from `gaugeVars`: the app provides it as the JavaScript value `window._ecuDA` (feet). Parse it with `parseFloat(window._ecuDA)` and treat NaN as missing. (DS1 also lists a `daft` "Density Alt" monitor; use `window._ecuDA` in screens.)

**Custom channels**: `customresult0` ... `customresult23` are user-defined DS1 results; what they mean depends on the user's setup. In the V8 export `customresult10` / `11` / `12` are named "LPFP Safety", "STFT Safety", "Knock Safety" (scaled x-0.1, offset -1; safety-warning results), and the example screens also use `customresult5` (nitrous %), `customresult10` (DI reduction) and `customresult14` (PI ms): always ask the user what a custom channel means before using it.

## V8 vs RS3 / TT RS: names that differ
| thing | 6/7/8 series (V8) | RS3 / TT RS (2.5 TFSI) |
|---|---|---|
| cylinders | 8, two banks (`B1` / `B2`, names with `2`) | 5 inline, single bank (no `2` variants) |
| knock / ignition per cyl | `wkrv`..`wkrv_8`, `zwcalcar`..`zwcalcar_8` | `wkrv`..`wkrv_5`, `zwcalcar`..`zwcalcar_5` |
| knock average | `wkrma` | `wkrmav` |
| target manifold pressure | `psrs_w` (and `pvds_w`) | `pvds_w` only |
| oil temp | `toel` (C) | `toelk_w` (C) |
| HPFP act / target | `prroh_w`, `prroh2_w` / `prsoll_w`, `prsoll2_w` | `prroh_w` / `prsoll_w` |
| lambda | `lamsoni_w`, `lamsoni2_w` | `lamsoni_w` |
| LPFP duty final | `PSP_rPS_mp` | `PSP_rPs` |
| intake manifold abs pressure | `psrg_w` | `psrg_w` |
| accel / lateral | `Com_aLng` / `Com_aTrnvrs` | same |

## Commonly used variables
| purpose | name | notes |
|---|---|---|
| engine speed | `nmot_w` | rpm |
| gear | `gangi` | |
| pedal | `wped_w` | % |
| load | `rl_w` | % relative load |
| boost actual / ambient / target | `psrg_w` / `pu_w` / `psrs_w` (V8), `pvds_w` (RS3 target) | absolute pressures in hPa; psi over ambient = `(psrg_w - pu_w) * 0.0145038` |
| LPFP actual / target | `pbkist_w` / `pbksoll_w` | kPa (`/100` = bar); limit around 580 kPa on a V8 |
| HPFP actual / target | `prroh_w`, `prroh2_w` / `prsoll_w`, `prsoll2_w` | MPa; `2` = bank 2 (V8) |
| lambda | `lamsoni_w`, `lamsoni2_w` | bank 1 / 2; a wideband not ready reads ~16: cap or hide above ~2 |
| ignition, average | `zwist` | deg |
| ignition per cylinder | `zwcalcar`, `zwcalcar_2` ... | deg, firing-order numbered |
| knock correction per cylinder | `wkrv`, `wkrv_2` ... | deg, <= 0, firing-order numbered |
| ECU torque | `miist_w` | |
| temps | `tans` (intake), `toel` / `toelk_w` (oil, C), `tmot` (coolant), `Gbx_tOilConv` (trans) | C |
| WGDC | `tvldste_w` | % |
| ethanol | `ethanolpercent` | % |
| battery | `ubsq` | V |
| map switch | `mapswitch` | |
| speeds | `vfzg_w`, `VehV_vWhlFrtL/FrtR/RrL/RrR` | |
| accel | `Com_aLng` | m/s^2 |
| custom channels | `customresult1` ... (e.g. 5 = nitrous %, 10 = DI reduction, 14 = PI ms in the example setup) | **meaning is defined by the user's DS1 setup**: ask |
| app values | `window.bT.carWeight` (lb), `window._ecuDA` (density altitude), `window.bT.carModel` | not in gaugeVars |

## Cylinder numbering is firing order
The numbered variables follow the engine's firing order, not the physical cylinder order. Variable index k (0 = unsuffixed) belongs to physical cylinder FO[k]:
- **V8 (6/7/8 series)**: FO = 1-5-4-8-6-3-7-2: `wkrv`=cyl 1, `_2`=5, `_3`=4, `_4`=8, `_5`=6, `_6`=3, `_7`=7, `_8`=2. Per physical cylinder 1..8: `["wkrv","wkrv_8","wkrv_6","wkrv_3","wkrv_2","wkrv_5","wkrv_7","wkrv_4"]`.
- **2.5 TFSI (RS3 / TT RS)**: FO = 1-2-4-5-3: `["wkrv","wkrv_2","wkrv_5","wkrv_3","wkrv_4"]`.
- Other engines: ask the user for the firing order before labelling cylinders.

## Handy conversions
- boost psi = `(psrg_w - pu_w) * 0.0145037738`
- kPa -> bar `/100`; C -> F `c*9/5+32`
