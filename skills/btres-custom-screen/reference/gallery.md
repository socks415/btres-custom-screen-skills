# The bTres Screen Gallery (gallery.betterthan.shop)

**https://gallery.betterthan.shop** is where the bTres community uploads, shares and manages custom screens. It holds two kinds of screen: **data screens** (the JSON gauge layouts this skill builds) and **boot screens** (the image or video a unit shows at power-on). Anyone can browse and download; a free account is needed to download and to publish. A unit installs a screen from the gallery or from a downloaded file.

## Getting a screen from this skill into the gallery
1. Build the screen (`scripts/make_screen.py`) and preview it.
2. Make **preview media** at the unit's exact resolution (see below): a screenshot from `preview.py` is a good start for an S-series screen; for an M1 / X1 screen use the scaled 800x480 preview.
3. Sign in at gallery.betterthan.shop, open **Upload screen**, choose **Data screen**, and fill the form.
4. Check it on a real unit before marking it Public.

## Accounts and publishing
- Register for a free account (name and email). Tick **"I'd like to publish my own screens"** to become a publisher (display name and phone required; the display name is public and unique).
- A new publisher is **pending**: they can upload, but screens stay **Private** (visible only to the owner and admins) until an admin approves the account. After approval they can set a screen to **Public**. Existing members can apply from the account menu.
- Admins approve publishers and can feature or hide screens. Approval and rejection notices come by email.
- Publishers can edit and delete only their own screens. Deleting is a soft delete (download history is kept and shows "(deleted)").

## Uploading a data screen
The **screen type is chosen at upload and cannot be changed** later.

| field | rules |
|---|---|
| Title | required, max 60 characters |
| Device target | **All S-series** (S1 / S2 / S2 Pro), **S2 Pro only**, or **All M1 / X1** |
| Cars | at least one: Audi 6/7/8 series, Audi R8, Audi RS3 / TTRS |
| Preview media | one or more JPG, PNG or MP4, ordered (the first is the cover); up to **12** per screen. Must be **exactly the display's resolution: 1920x480 (S-series) or 800x480 (M1 / X1)**; other sizes are refused |
| Screen file | exactly one `.json` screen file (or a `.zip` for a screen that bundles images; see limits), which must parse |
| Requires a custom tune | checkbox: downloaders see a warning and must confirm before downloading |
| Description / Requirements | free text (max 1200 / 800 characters); list the DS1 monitors or custom channels the screen needs, and mention if it uses `btScreen` (saved settings / keyboard), which needs a bTres app version that has it |

**Limits**: image 10 MB, MP4 60 MB, screen JSON **1 MB**, ZIP 20 MB (200 MB unpacked, 500 files). Uploads are checked by file signature, not extension. This is why the skill keeps screens under 1.00 MB.

**Security scan**: every data screen file is scanned before it is trusted. It flags links and URLs, `fetch` / `XMLHttpRequest` / `WebSocket` calls, external scripts, code assembled at run time (computed `eval`, `window['fe'+'tch']`, ...), obfuscated payloads (base64 is decoded and scanned again), and data hidden in images. Normal local `eval` of a string literal (how bTres screens start their code) is reported as informational only. Screens from `make_screen.py` embed their code as a plain string literal and scan clean; a screen with network calls or hidden code will be flagged. Don't add any.

## Boot screens
A boot screen is a single JPG, PNG or MP4 (no JSON): All S-series or All M1 / X1 (no "S2 Pro only"). It has no cars, tune flag or description. This skill doesn't build them.

## Browsing, downloading, favorites
- Filters: device, car, custom-tune, publisher, sort by last updated or title. Featured screens show first.
- A first visit shows a community disclaimer (screens are made by members, not by Better Than).
- Download gives the JSON (data) or image / video (boot). A custom-tune screen asks for confirmation first.
- Favorites are kept on the account (or in the browser when logged out).
- A unit can download straight from the gallery using its registered **device id** (the device API); a screen is then installed from the unit's own screen list.

## Publisher dashboard
**My screens**: one row per screen (cover, title, type, device, resolution, downloads in the last 30 days and unique users, last updated) with View / Edit / Delete. **Downloads**: a report over a date range (total and unique downloads with change vs the previous period, downloads per day, top screens, a searchable download log). Your own downloads of your screens are not counted.

## Handover checklist for an AI using this skill
- Tell the user the screen can be uploaded at https://gallery.betterthan.shop and what to prepare: the `.json`, preview media at the exact resolution, device target, cars, whether it needs a custom tune, and a requirements note naming the DS1 monitors / custom channels used.
- Say that new publishers start Private until approved, and that screens should be tested on a real unit before going Public.
- Never claim the screen has been uploaded or approved; this skill doesn't upload for the user.
