#!/usr/bin/env python3
"""Build the private 'Road to Winnipeg' site from data/stops.json.

Usage:  python3 build.py
Writes: index.html, itinerary/index.html, route-map/index.html

Everything on the site is generated from data/stops.json. To change a stop,
edit the JSON and re-run this script, then ./deploy.sh
"""
import json, os, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(ROOT, "data", "stops.json")))
META, STOPS, ORIGIN = DATA["meta"], DATA["stops"], DATA["origin"]

BUILT = datetime.date.today().strftime("%B %-d, %Y")


def d(s):
    return datetime.date.fromisoformat(s)


def fmt(s, year=False):
    dt = d(s)
    return dt.strftime("%b %-d, %Y") if year else dt.strftime("%a %b %-d")


def span(a, b):
    da, db = d(a), d(b)
    if da.month == db.month:
        return f"{da.strftime('%b %-d')}\u2013{db.strftime('%-d')}"
    return f"{da.strftime('%b %-d')} \u2013 {db.strftime('%b %-d')}"


def head(title, css="assets/css/site.css"):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="robots" content="noindex, nofollow, noarchive, nosnippet" />
<meta name="referrer" content="no-referrer" />
<title>{title}</title>
<link rel="stylesheet" href="{css}" />
</head>
<body>
<div class="privacy"><b>Private</b> &nbsp;&middot;&nbsp; unlisted companion to the caravan &mdash; not linked from the public site, not indexed</div>
"""


def hero(h1, sub, home=None, eyebrow=None):
    back = f'<a class="home-link" href="{home}">&larr; Road to Winnipeg</a>' if home else ""
    eb = f'<p class="eyebrow">{eyebrow}</p>' if eyebrow and not home else ""
    return f"""<header class="site-hero">
  <div class="aurora-band" aria-hidden="true"></div>
  <div class="wrap site-hero-inner">
    {back}{eb}
    <h1>{h1}</h1>
    <p class="sub">{sub}</p>
"""


def foot(rel=""):
    return f"""<footer class="site-foot">
  <div class="wrap">
    <p><b>The Road to Winnipeg</b> &middot; <a href="{rel}index.html">Overview</a> &middot;
       <a href="{rel}itinerary/">Itinerary</a> &middot; <a href="{rel}route-map/">Route map</a>
       &middot; <span style="color:var(--stone)">built {BUILT}</span></p>
    <p class="fine">Private trip log for the run up to the 2026 Northern Lights &amp; Polar Bears rendezvous.
      Personal document by SN Thorsen &mdash; not affiliated with or representing Airstream Club International
      or any other club or organization. Unlisted by choice; share the link or don't.</p>
  </div>
</footer>
</body>
</html>
"""


def progress_js(var="TRIP"):
    """Date-driven progress shared by every page."""
    compact = [{"n": s["n"], "name": s["name"], "town": s["short"],
                "arrive": s["arrive"], "depart": s["depart"],
                "lat": s["lat"], "lon": s["lon"]} for s in STOPS]
    return (f"var {var}=" + json.dumps(compact, separators=(",", ":")) + ";\n"
            + f'var TRIP_START="{META["start"]}",TRIP_END="{META["end"]}";\n'
            + """
function tripDay(s){return new Date(s+"T12:00:00");}
function tripToday(){var n=new Date();return new Date(n.getFullYear(),n.getMonth(),n.getDate(),12,0,0);}
function tripState(){
  var t=tripToday(),start=tripDay(TRIP_START),end=tripDay(TRIP_END),MS=86400000;
  var cur=-1;
  for(var i=0;i<TRIP.length;i++){ if(tripDay(TRIP[i].arrive)<=t) cur=i; }
  var total=Math.round((end-start)/MS)+1;
  if(t<start) return {phase:"before",days:Math.round((start-t)/MS),total:total};
  if(t>end)   return {phase:"after",total:total};
  return {phase:"on",idx:cur,stop:TRIP[cur],day:Math.floor((t-start)/MS)+1,total:total};
}
function tripBanner(el){
  if(!el) return; var s=tripState();
  if(s.phase==="before"){
    el.innerHTML='<span class="tag-live soon"></span> Rolls out of Xenia in <b>'+s.days+
      ' day'+(s.days===1?'':'s')+'</b><span class="where">'+s.total+' days and 2,348 miles to the Winnipeg rendezvous</span>';
  } else if(s.phase==="after"){
    el.innerHTML='<span class="tag-live done"></span> <b>Arrived Winnipeg</b>'+
      '<span class="where">The caravan has the schedule from here</span>';
  } else {
    var leaving=tripDay(s.stop.depart), t=tripToday(), MS=86400000;
    var out=Math.round((leaving-t)/MS);
    var tail = out<=0 ? 'moving on today' : (out===1?'rolling on tomorrow':'here '+out+' more nights');
    el.innerHTML='<span class="tag-live on"></span> <b>Day '+s.day+' of '+s.total+'</b> &middot; parked at <b>'+
      s.stop.town+'</b><span class="where">Stop '+s.stop.n+' of 13 &middot; '+
      s.stop.name+' &middot; '+tail+'</span>';
  }
}
""")


# ---------------------------------------------------------------- index
def build_index():
    hrs, mins = divmod(META["drive_minutes"], 60)
    route = ' <span class="arr">&rarr;</span> '.join(
        ['<b>Xenia</b>'] + [s["short"] for s in STOPS[:-1]] + ['<b>Winnipeg</b>'])

    rows = []
    for s in STOPS:
        flag = ""
        if s.get("arrival"):
            flag = ' <span style="color:var(--aurora-deep);font-weight:700">&#9733;</span>'
        elif s.get("highlight"):
            flag = ' <span style="color:var(--amber-deep);font-weight:700">&bull;</span>'
        rows.append(
            f'<tr data-arrive="{s["arrive"]}" data-depart="{s["depart"]}">'
            f'<td>{s["n"]}. {s["short"]}{flag}</td>'
            f'<td>{span(s["arrive"], s["depart"])}</td>'
            f'<td>{s["nights"]}</td>'
            f'<td>{s["miles"]:,.0f}</td>'
            f'<td>{s["drive"]}</td>'
            f'<td>{s["name"]}</td></tr>')

    return (head("The Road to Winnipeg — private trip log")
        + hero('The Road to <span class="amp">Winnipeg</span>',
               'The private half of the caravan year &mdash; 2,348 miles from the driveway in Xenia '
               'to the rendezvous at Town &amp; Country, and everything that has to go right first.',
               eyebrow="Private companion &middot; Aug 13 – Sep 12, 2026")
        + f"""    <div class="route-line">{route}</div>
    <div class="stats">
      <div class="stat"><div class="n">13</div><div class="l">Stops</div></div>
      <div class="stat"><div class="n">2,348</div><div class="l">Miles</div></div>
      <div class="stat"><div class="n">30</div><div class="l">Nights</div></div>
      <div class="stat"><div class="n">{hrs}h {mins:02d}m</div><div class="l">Driving</div></div>
      <div class="stat"><div class="n">5+1</div><div class="l">States, province</div></div>
    </div>
  </div>
</header>

<main class="wrap">
  <div id="trip-status" class="trip-status">Loading trip progress&hellip;</div>

  <div class="grid">
    <a class="card" href="itinerary/">
      <span class="kicker">Stop by stop</span>
      <h2>The Itinerary</h2>
      <p>All thirteen stops with dates, drive times, hookups, and what the trailer needs at each one.</p>
      <span class="go">Open the itinerary</span>
    </a>
    <a class="card" href="route-map/">
      <span class="kicker">Where we are</span>
      <h2>Route Map</h2>
      <p>The whole run drawn on one map, with progress that advances by date on its own.</p>
      <span class="go">Open the map</span>
    </a>
  </div>

  <div class="sec-head">
    <span class="kicker">At a glance</span>
    <h2>The shape of the run</h2>
    <p>Thirty nights, front-loaded with short overnights and back-loaded with two long stays &mdash;
       six nights at the Minot rally and a full week at Metigoshe before the border.</p>
  </div>

  <div class="panel">
    <div class="table-scroll">
    <table class="spec">
      <tr><th>Stop</th><th>Dates</th><th>Nights</th><th>Leg miles</th><th>Drive</th><th>Campground</th></tr>
      {''.join(rows)}
    </table>
    </div>
  </div>

  <div class="sec-head">
    <span class="kicker">The three that matter</span>
    <h2>What this route actually asks of the trailer</h2>
  </div>

  <div class="panel amber">
    <span class="kicker">Aug 28 – Sep 1</span>
    <h2>Four nights without shore power</h2>
    <p>Juniper and Cottonwood are back to back in Theodore Roosevelt National Park, and neither has hookups.
       Juniper at least has drinking water and a fill-and-dump station open through October 1;
       <strong>Cottonwood has neither</strong> &mdash; seasonal water and nothing else, no dump on site.
       Arrive at Juniper empty, leave it full, and treat the two nights at Cottonwood as the real test of
       200&nbsp;Ah and the Onan.</p>
    <p>Generator hours in both units are <strong>8&nbsp;a.m. to 8&nbsp;p.m.</strong> with an effective muffler.
       That is the whole window &mdash; a mid-day run inside it covers the day easily, and the Truma on LP
       means the furnace and hot water never touch the batteries.</p>
  </div>

  <div class="panel amber">
    <span class="kicker">Sep 12</span>
    <h2>The border, at Pembina–Emerson</h2>
    <p>I-29 north out of Cavalier, into Canada at <strong>Pembina&ndash;Emerson</strong> &mdash;
       open 24/7, four auto lanes, the busiest crossing in North Dakota and one of only three in the state
       that never closes. On the far side it becomes Highway 75 and runs straight north to the Winnipeg
       Perimeter.</p>
    <p>What has to be settled before the booth: tanks dumped, <strong>fresh produce and meat eaten or gone</strong>,
       <strong>no firewood</strong>, alcohol inside the personal exemption (1.5&nbsp;L wine <em>or</em> 1.14&nbsp;L spirits
       <em>or</em> 8.5&nbsp;L beer per adult), passports and the dog's rabies certificate reachable from the driver's seat.
       All food, plant and animal products must be declared &mdash; failing to declare runs to a $1,300 penalty.</p>
  </div>

  <div class="panel green">
    <span class="kicker">Sep 12–13</span>
    <h2>Arriving a day early</h2>
    <p>The caravan rendezvous is Sunday the 13th at site 165. The plan puts the trailer on the pad
       <strong>Saturday the 12th</strong> &mdash; level, hooked up and settled before the first handshake, with a full
       day of slack if the border takes three hours instead of one.</p>
    <p>One local note that carries over from the caravan research: Town &amp; Country is 56001 Murdock Road and
       <strong>Lyncrest Airport (CJL5) is 57119 Murdock Road</strong>, 2.9&nbsp;km up the same road with two grass
       runways and club circuit traffic overhead. Sub-250&nbsp;g exempts the Mini 4K from registration and the
       distance rules; it does not exempt it from the hazard rule. Not at the rendezvous.</p>
  </div>

  <div class="panel dark">
    <span class="kicker">About this site</span>
    <h2>Why it lives here and not there</h2>
    <p>The public caravan site covers the caravan &mdash; the 31 days from the Winnipeg rendezvous to Churchill
       and back, written for twenty families. This one covers the month before it, which is nobody's business
       but ours: a shakedown run, a rally, two national park units and a border crossing.</p>
    <p>It is a separate site on a separate repository. Nothing on the public site links here, nothing here is
       indexed by search engines, and no roster, phone number or personal detail belonging to anyone else
       appears on it. Share the link with whoever should have it.</p>
  </div>
</main>
"""
        + f"""<script>
{progress_js()}
tripBanner(document.getElementById('trip-status'));
(function(){{
  var t=tripToday();
  document.querySelectorAll('tr[data-arrive]').forEach(function(tr){{
    var a=tripDay(tr.dataset.arrive), b=tripDay(tr.dataset.depart);
    if(t>=a && t<b) tr.classList.add('now');
  }});
}})();
</script>
"""
        + foot())


# ------------------------------------------------------------ itinerary
def build_itinerary():
    jumps = "".join(
        f'<a href="#s{s["n"]}" data-arrive="{s["arrive"]}" data-depart="{s["depart"]}">'
        f'{s["short"]}</a>' for s in STOPS)

    legs = []
    prev_town = ORIGIN["name"]
    for s in STOPS:
        cls = ["leg"]
        if s.get("highlight"):
            cls.append("is-highlight")
        if s.get("arrival"):
            cls.append("is-arrival")
        if s.get("border"):
            cls.append("is-border")

        pills = "".join(
            f'<span class="pill{" warn" if f.lower().startswith("no ") or "8a" in f.lower() else ""}">{f}</span>'
            for f in s["features"])
        notes = "".join(f'<h3>{n["h"]}</h3><p>{n["p"]}</p>' for n in s["notes"])

        contact = []
        if s.get("phone"):
            contact.append(f'<span>{s["phone"]}</span>')
        if s.get("url"):
            contact.append(f'<a href="{s["url"]}" target="_blank" rel="noopener noreferrer">Campground page</a>')
        contact.append(f'<span class="coords">{s["lat"]:.5f}, {s["lon"]:.5f}</span>')

        nights = f'{s["nights"]} night' + ("" if s["nights"] == 1 else "s")
        legs.append(f"""<article class="{' '.join(cls)}" id="s{s['n']}"
         data-arrive="{s['arrive']}" data-depart="{s['depart']}">
  <span class="node" aria-hidden="true"></span>
  <div class="leg-head">
    <div class="leg-eyebrow">Stop {s['n']} &middot; {s['kicker']}<span class="now"></span></div>
    <h2 class="leg-town">{s['name']}</h2>
    <p class="leg-place">{s['town']}</p>
    <div class="leg-meta">
      <span><b>{fmt(s['arrive'])}</b> &rarr; <b>{fmt(s['depart'])}</b></span>
      <span>{nights}</span>
      <span>mile <b>{s['cum']:,.0f}</b> of 2,348</span>
    </div>
  </div>
  <div class="drive">{prev_town} &rarr; here &nbsp;&middot;&nbsp; {s['miles']:,.1f} mi &nbsp;&middot;&nbsp; {s['drive']}</div>
  <div class="pill-row">{pills}</div>
  <div class="leg-body">
    {notes}
    <div class="leg-foot">
      <span>{s['address']}</span>
      {''.join(contact)}
    </div>
  </div>
</article>""")
        prev_town = s["short"]

    return (head("Itinerary — The Road to Winnipeg", "../assets/css/site.css")
        + hero("Itinerary",
               "Thirteen stops, thirty nights, Xenia to the Winnipeg rendezvous. "
               "Today's stop is marked automatically.",
               home="../index.html")
        + """  </div>
</header>

<div class="controls">
  <div class="wrap controls-inner">
    <nav class="jump" id="jump">""" + jumps + """</nav>
    <button class="btn" onclick="window.print()">Print</button>
  </div>
</div>

<main class="wrap">
  <div id="trip-status" class="trip-status">Loading trip progress&hellip;</div>
  <div class="route">
""" + "\n".join(legs) + """
  </div>
</main>
""" + f"""<script>
{progress_js()}
tripBanner(document.getElementById('trip-status'));
(function(){{
  var t=tripToday();
  document.querySelectorAll('.leg').forEach(function(el){{
    var a=tripDay(el.dataset.arrive), b=tripDay(el.dataset.depart);
    if(t>=b) el.classList.add('is-past');
    if(t>=a && t<b){{
      el.classList.add('is-now');
      var tag=el.querySelector('.leg-eyebrow .now');
      if(tag) tag.innerHTML=' &middot; here now';
    }}
  }});
  document.querySelectorAll('#jump a').forEach(function(el){{
    var a=tripDay(el.dataset.arrive), b=tripDay(el.dataset.depart);
    if(t>=a && t<b) el.classList.add('is-now');
  }});
}})();
</script>
""" + foot("../"))


# ------------------------------------------------------------ route map
def build_map():
    pts = [{"name": "Xenia", "lat": ORIGIN["lat"], "lon": ORIGIN["lon"],
            "dates": "Departs " + fmt(ORIGIN["depart"]), "camp": "Home",
            "note": "Where the whole thing starts", "kind": "origin", "arrive": META["start"],
            "dir": ORIGIN.get("label_dir", "bottom")}]
    for s in STOPS:
        pts.append({
            "name": s["short"],
            "lat": s["lat"], "lon": s["lon"],
            "dates": span(s["arrive"], s["depart"]),
            "camp": s["name"],
            "note": s["notes"][0]["h"],
            "kind": "arrival" if s.get("arrival") else ("big" if s.get("highlight") else ""),
            "dir": s.get("label_dir", "right"),
            "arrive": s["arrive"]})

    return (head("Route Map — The Road to Winnipeg", "../assets/css/site.css")
        + '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />\n'
        + hero("Route Map",
               "Xenia to the Winnipeg rendezvous, drawn straight from the trip file. "
               "Progress advances by date on its own.",
               home="../index.html")
        + """  </div>
</header>

<main class="wrap">
  <div id="trip-status" class="trip-status">Loading trip progress&hellip;</div>
  <div id="map" class="route-map"></div>
  <div class="map-legend">
    <span><i class="lg road-t"></i> Traveled</span>
    <span><i class="lg road-u"></i> Still to come</span>
    <span><i class="lg cur"></i> Parked here now</span>
    <span><i class="lg fin"></i> Rendezvous</span>
  </div>
  <p class="map-note">Straight lines between stops, not the driving route &mdash; the turn-by-turn lives in the
    trip file. Tap any stop for dates and campground. The line crosses into Canada at Pembina&ndash;Emerson
    on the last leg.</p>
</main>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
""" + f"""<script>
{progress_js()}
var PTS={json.dumps(pts, separators=(",", ":"))};
tripBanner(document.getElementById('trip-status'));
(function(){{
  var t=tripToday();
  var map=L.map('map',{{scrollWheelZoom:false}});
  L.tileLayer('https://{{s}}.basemaps.cartocdn.com/rastertiles/voyager/{{z}}/{{x}}/{{y}}.png',
    {{attribution:'&copy; OpenStreetMap contributors &copy; CARTO',subdomains:'abcd',maxZoom:11,minZoom:3}}).addTo(map);
  map.fitBounds(PTS.map(function(p){{return [p.lat,p.lon];}}),{{padding:[36,36]}});

  var cur=-1;
  for(var i=0;i<PTS.length;i++){{ if(tripDay(PTS[i].arrive)<=t) cur=i; }}

  for(var j=0;j<PTS.length-1;j++){{
    var a=PTS[j],b=PTS[j+1],traveled=(j+1)<=cur;
    L.polyline([[a.lat,a.lon],[b.lat,b.lon]],
      traveled ? {{color:'#9c5f12',weight:4,opacity:.95}}
               : {{color:'#5b6b7d',weight:3,opacity:.65,dashArray:'6,8'}}).addTo(map);
  }}

  PTS.forEach(function(p,i){{
    var arrival=p.kind==='arrival', big=p.kind==='big', origin=p.kind==='origin';
    var color=arrival?'#1c8a64':(big?'#d98a2b':(origin?'#6c7787':'#34618f'));
    var m=L.circleMarker([p.lat,p.lon],
      {{radius:arrival?9:(big?8:6),color:'#fff',weight:2,fillColor:color,fillOpacity:1}}).addTo(map);
    m.bindPopup('<div class="pop"><b>'+p.name+'</b>'+(arrival?' &#9733;':'')+
      '<br><span class="pd">'+p.dates+'</span><br>'+p.camp+
      '<br><span class="pn">'+p.note+'</span></div>');
    var off={{right:[9,0],left:[-9,0],top:[0,-8],bottom:[0,8]}}[p.dir]||[9,0];
    m.bindTooltip(p.name,{{permanent:true,direction:p.dir,className:'stoplbl',offset:off}});
  }});

  var st=tripState();
  if(st.phase==='on'&&cur>=0){{
    var c=PTS[cur];
    var ic=L.divIcon({{className:'',html:'<div class="pulse"></div>',iconSize:[16,16],iconAnchor:[8,8]}});
    L.marker([c.lat,c.lon],{{icon:ic,zIndexOffset:1000}}).addTo(map)
      .bindPopup('<div class="pop"><b>We are here</b><br><span class="pn">'+c.camp+'</span></div>');
  }}
}})();
</script>
""" + foot("../"))


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(text)
    print(f"  wrote {path}  ({len(text):,} bytes)")


if __name__ == "__main__":
    print("Building The Road to Winnipeg…")
    write("index.html", build_index())
    write("itinerary/index.html", build_itinerary())
    write("route-map/index.html", build_map())
    print("Done. Next:  ./deploy.sh")
