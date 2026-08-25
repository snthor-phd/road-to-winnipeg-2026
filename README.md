# The Road to Winnipeg

Private companion site for the run from Xenia, Ohio to the 2026 Northern Lights & Polar Bears
rendezvous at Town & Country Campground, Winnipeg — **Aug 13 – Sep 12, 2026**, 13 stops, 2,348 miles.

Deliberately separate from the public caravan site at `snthor-phd/polar-bears-2026`:
nothing there links here, `robots.txt` disallows everything, and every page carries
`noindex, nofollow`. Unlisted, not secret — anyone with the URL can read it, so keep the URL close.

## How it is built

Everything comes from `data/stops.json`. `build.py` renders three static pages from it.

```
data/stops.json      the only file you edit for content
build.py             renders index.html, itinerary/index.html, route-map/index.html
assets/css/site.css  theme — same palette as the caravan site, amber accent instead of aurora
deploy.sh            commit, push, enable Pages
```

To change anything about a stop — dates, mileage, hookups, the notes — edit `data/stops.json`
and re-run:

```bash
python3 build.py
./deploy.sh
```

Do not hand-edit the generated `index.html`, `itinerary/index.html` or `route-map/index.html`;
the next build overwrites them.

### Stop fields

| Field | Meaning |
|---|---|
| `n` | order, 1–13 |
| `short` | compact label used on the map, the jump nav, and the summary table |
| `kicker` | small line above the stop name on the itinerary |
| `arrive` / `depart` | ISO dates — these drive all the progress logic |
| `miles` / `cum` / `drive` | leg distance, running total, drive time |
| `features` | pills; anything starting "No " renders as a warning pill |
| `notes` | list of `{h, p}` — heading and paragraph |
| `label_dir` | map tooltip direction: right / left / top / bottom |
| `highlight` / `arrival` / `border` | styling flags for the rally, Metigoshe, and the last two stops |

## Progress

Every page works out where the trip is from today's date in the browser — no build step, no
server. Before Aug 13 it counts down; between Aug 13 and Sep 12 it names the current stop and
how many nights are left there; after Sep 12 it says the caravan has taken over.

Nothing needs to be redeployed as the trip moves.

## Source

Built from the RV LIFE trip file `trip2608251851.xlsx` (Trip Summary + Turn By Turn Directions),
trimmed to the legs before the caravan starts. Campground details verified against the operators'
own pages; border and national-park rules against CBSA and NPS.
