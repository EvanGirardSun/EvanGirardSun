"""Render the profile from public GitHub activity and recorded drone telemetry."""
import argparse
import csv
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
import io
import json
import math
from pathlib import Path
import re
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OWNER = "EvanGirardSun"
FLIGHT_URL = f"https://raw.githubusercontent.com/{OWNER}/phi-lab-autonomy/main/logs/run_20261014_232303.csv"
PALETTES = {
    "dark": dict(bg="#0d1117", fg="#c9d1d9", muted="#8b949e", grid="#212b36", blue="#58a6ff", green="#3fb950", purple="#bc8cff"),
    "light": dict(bg="#ffffff", fg="#1f2328", muted="#656d76", grid="#d8dee4", blue="#0969da", green="#1a7f37", purple="#8250df"),
}


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.days, self.target, self.words = {}, None, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "td" and "data-date" in a:
            date.fromisoformat(a["data-date"])
            self.days[a["id"]] = {"date": a["data-date"], "level": int(a["data-level"])}
        if tag == "tool-tip" and a.get("for") in self.days:
            self.target, self.words = a["for"], []

    def handle_data(self, data):
        if self.target is not None:
            self.words.append(data)

    def handle_endtag(self, tag):
        if tag == "tool-tip" and self.target is not None:
            label = " ".join(self.words).strip()
            match = re.search(r"([\d,]+) contributions?", label)
            if label.startswith("No contributions"):
                count = 0
            elif match:
                count = int(match[1].replace(",", ""))
            else:
                raise ValueError(f"Unrecognized contribution label: {label}")
            self.days[self.target]["count"] = count
            self.target = None

    def result(self):
        days = sorted(self.days.values(), key=lambda d: d["date"])
        if not days or any("count" not in day or not 0 <= day["level"] <= 4 for day in days):
            raise ValueError("Incomplete public contribution calendar")
        if len({day["date"] for day in days}) != len(days):
            raise ValueError("Duplicate contribution date")
        return days


def fetch(url):
    req = Request(url, headers={"User-Agent": "EvanGirardSun-profile", "Accept": "text/html,text/plain"})
    with urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8")


def refresh():
    parser = CalendarParser()
    parser.feed(fetch(f"https://github.com/users/{OWNER}/contributions"))
    days = parser.result()
    if len(days) < 300:
        raise ValueError("Expected a full public contribution calendar")
    flight = fetch(FLIGHT_URL)
    rows = list(csv.DictReader(io.StringIO(flight)))
    if not rows or not {"t", "state", "px", "py", "pz"}.issubset(rows[0]):
        raise ValueError("Unexpected telemetry columns")
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data/public-activity.json").write_text(json.dumps({
        "updated": datetime.now(timezone.utc).date().isoformat(), "days": days}, indent=2) + "\n", encoding="utf-8", newline="\n")
    canonical=io.StringIO(newline="")
    writer=csv.DictWriter(canonical,fieldnames=list(rows[0]),lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    (ROOT / "data/follow-session.csv").write_text(canonical.getvalue(), encoding="utf-8", newline="\n")


def font(size, bold=False, mono=False):
    paths = (["C:/Windows/Fonts/consola.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"] if mono else
             ["C:/Windows/Fonts/segoeuib.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if bold else
             ["C:/Windows/Fonts/segoeui.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"])
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def text(d, xy, value, size, fill, **kwargs):
    d.text(xy, value, font=font(size, **kwargs), fill=fill, anchor="lt")


def follow_rows():
    with (ROOT / "data/follow-session.csv").open(newline="") as stream:
        rows = [r for r in csv.DictReader(stream) if r["state"] == "FOLLOW"]
    if not rows:
        raise ValueError("No FOLLOW phase in the recording")
    return rows


def lorenz_trace():
    point = (0.1, 0.0, 0.0)
    def derivative(p):
        x,y,z=p
        return (10*(y-x), x*(28-z)-y, x*y-8*z/3)
    trace=[]
    dt=0.008
    for i in range(6500):
        k1=derivative(point)
        k2=derivative(tuple(a+dt*b/2 for a,b in zip(point,k1)))
        k3=derivative(tuple(a+dt*b/2 for a,b in zip(point,k2)))
        k4=derivative(tuple(a+dt*b for a,b in zip(point,k3)))
        point=tuple(a+dt*(b+2*c+2*d+e)/6 for a,b,c,d,e in zip(point,k1,k2,k3,k4))
        if i>800:
            x,y,z=point
            trace.append((984+7.8*x+1.2*y, 259-4.7*z))
    return trace


def header(theme, trace, cursor=None):
    p = PALETTES[theme]
    image = Image.new("RGB", (1280, 280), p["bg"])
    d = ImageDraw.Draw(image)
    text(d, (32, 25), "EVANGIRARDSUN /", 19, p["muted"], mono=True)
    text(d, (28, 72), "Evan Girard–Sun", 64, p["fg"], bold=True)
    text(d, (33, 166), "Robot perception & control", 31, p["blue"])
    text(d, (33, 225), "Python  /  Computer vision  /  Autonomous systems", 19, p["muted"])
    # Lorenz phase portrait, independent of the flight-data dashboard.
    for i in range(6):
        y = 75 + i*31
        d.line((790, y, 1190, y), fill=p["grid"], width=1)
    d.line(trace, fill=p["blue"], width=1)
    point = trace[-1] if cursor is None else trace[cursor]
    d.ellipse((point[0]-5, point[1]-5, point[0]+5, point[1]+5), fill=p["green"])
    text(d, (795, 20), "LORENZ / PHASE SPACE", 16, p["muted"], mono=True)
    return image


def iso_calendar(d, days, p):
    first = date.fromisoformat(days[0]["date"])
    first -= timedelta(days=(first.weekday()+1)%7)
    colors = [p["grid"], "#155d36", "#238636", "#3fb950", "#7ee787"]
    if p is PALETTES["light"]:
        colors = ["#e6ebf0", "#b5dfb3", "#6dc477", "#2da44e", "#116329"]
    for day in days:
        when = date.fromisoformat(day["date"])
        week, weekday = (when-first).days//7, int(when.strftime("%w"))
        x, y = 48 + week*36 + weekday*15, 212 + week*4.2 - weekday*8
        h = 0 if not day["count"] else 5 + 10*math.log2(day["count"]+1)
        top = [(x,y-h), (x+31,y+3.6-h), (x+44,y-3.4-h), (x+13,y-7-h)]
        d.polygon([(x,y), (x+31,y+3.6), top[1], top[0]], fill="#1a4b30" if h else colors[0])
        d.polygon([(x+31,y+3.6),(x+44,y-3.4),top[2],top[1]], fill="#236440" if h else colors[0])
        d.polygon(top, fill=colors[day["level"]])


def dashboard(theme, activity, rows):
    p = PALETTES[theme]
    image = Image.new("RGB", (1280, 610), p["bg"])
    d = ImageDraw.Draw(image)
    text(d, (32, 18), "Development activity", 30, p["blue"])
    text(d, (680, 18), "Vision-guided flight", 30, p["blue"])
    recent=activity["days"][-84:]
    total = sum(day["count"] for day in recent)
    text(d, (32, 67), f"{total} public contributions / last 12 weeks", 21, p["muted"])
    text(d, (680, 67), "FOLLOW · 14 OCT 2026 · target-relative estimate", 18, p["muted"], mono=True)
    iso_calendar(d, recent, p)
    d.line((635, 20, 635, 565), fill=p["grid"], width=1)
    # Pose traces keep gaps where the estimator did not produce a sample.
    x0, x1, y0, y1 = 720, 1230, 126, 337
    start, end = float(rows[0]["t"]), float(rows[-1]["t"])
    for val in (-0.5, 0, 0.5, 1, 1.5):
        y = y1 - (val+0.6)/2.4*(y1-y0)
        d.line((x0, y, x1, y), fill=p["grid"], width=1)
        text(d, (673, y-10), f"{val:g}", 15, p["muted"], mono=True)
    for sec in (0, 20, 40, 60, 80):
        x = x0 + sec/(end-start)*(x1-x0)
        if x <= x1+5:
            d.line((x,y0,x,y1), fill=p["grid"], width=1)
            text(d, (x-10,y1+10), str(sec), 15, p["muted"], mono=True)
    for key, color in (("px",p["blue"]),("py",p["purple"]),("pz",p["green"])):
        segment = []
        for row in rows:
            if not row[key]:
                if len(segment)>1:
                    d.line(segment, fill=color, width=2)
                segment=[]
                continue
            t, v = float(row["t"])-start, float(row[key])
            segment.append((x0+t/(end-start)*(x1-x0), y1-(v+0.6)/2.4*(y1-y0)))
        if len(segment)>1:
            d.line(segment, fill=color, width=2)
    text(d, (720, 103), "position / m", 15, p["muted"], mono=True)
    text(d, (1145, 367), "time / s", 15, p["muted"], mono=True)
    for i, (label, color) in enumerate((("x",p["blue"]),("y",p["purple"]),("z",p["green"]))):
        x=710+i*70
        d.line((x,382,x+18,382), fill=color, width=3)
        text(d, (x+25,372), label, 18, p["muted"], mono=True)
    text(d, (32, 294), "Code paths", 24, p["fg"])
    for i,(name,label) in enumerate((("vision.py","AprilTag pose estimation"),
                                   ("control.py","State estimation + feedback"),
                                   ("link_server.py","Command transport + watchdog"))):
        y=350+i*64
        d.ellipse((34,y+6,41,y+13),fill=p["blue"])
        text(d,(55,y),name,22,p["blue"],mono=True)
        text(d,(55,y+28),label,18,p["muted"])
    for x, value, label in ((680,"14","Python source files"),(875,"5","Recorded sessions"),(1070,"9","Follow simulations")):
        text(d, (x,452),value,42,p["fg"],bold=True)
        text(d, (x,515),label,16,p["muted"])
    d.line((32,551,1248,551),fill=p["grid"],width=1)
    text(d,(32,572),"Python   OpenCV   NumPy   TensorFlow",20,p["blue"],mono=True)
    text(d,(1000,576),"UTC "+activity["updated"],16,p["muted"],mono=True)
    return image


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh",action="store_true",help="Refresh public data before rendering")
    args=parser.parse_args()
    if args.refresh:
        refresh()
    activity=json.loads((ROOT/"data/public-activity.json").read_text())
    rows=follow_rows()
    trace=lorenz_trace()
    for theme in PALETTES:
        base=header(theme,trace)
        base.save(ROOT/"assets"/f"research-header-{theme}.png",optimize=True)
        frames=[header(theme,trace,int(i*(len(trace)-1)/23)).quantize(colors=64) for i in range(24)]
        frames[0].save(ROOT/"assets"/f"research-header-{theme}.gif",save_all=True,append_images=frames[1:],
                       duration=[90]*23+[1600],loop=0,optimize=True)
        dashboard(theme,activity,rows).save(ROOT/"assets"/f"research-dashboard-{theme}.png",optimize=True)
    print("Rendered profile from public activity and recorded FOLLOW telemetry")


if __name__=="__main__":
    main()
