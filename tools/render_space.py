"""Draw paired inertial-orbit and Earth-fixed ground-track views for the profile."""
import math
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import orbit

ROOT = Path(__file__).resolve().parents[1]
S = 2
W, H = 1440, 650
PALETTES = {
    "dark": dict(bg="#0d1117", ink="#dce4ef", muted="#8190a4", faint="#263449",
                 blue="#81b9e5", dim="#3f6381", amber="#dab884", globe="#142337"),
    "light": dict(bg="#ffffff", ink="#23374d", muted="#64758a", faint="#dce5ee",
                  blue="#276898", dim="#8ba9c0", amber="#9a6527", globe="#eef4f9"),
}
AZ, EL = math.radians(33), math.radians(22)
RIGHT = (-math.sin(AZ), math.cos(AZ), 0)
UP = (-math.sin(EL)*math.cos(AZ), -math.sin(EL)*math.sin(AZ), math.cos(EL))
LOOK = (math.cos(EL)*math.cos(AZ), math.cos(EL)*math.sin(AZ), math.sin(EL))
ORIGIN, SCALE = (340, 404), 0.0090
LAND = json.loads((ROOT/"data/land-110m.json").read_text(encoding="utf-8"))["rings"]


def font(size, bold=False, mono=False):
    names = (["C:/Windows/Fonts/consola.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"] if mono else
             ["C:/Windows/Fonts/segoeuib.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if bold else
             ["C:/Windows/Fonts/segoeui.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"])
    for path in names:
        if Path(path).exists():
            return ImageFont.truetype(path, round(size*S))
    return ImageFont.load_default(size=round(size*S))


def line(d, points, color, width=1):
    if len(points)>1:
        d.line([(x*S,y*S) for x,y in points], fill=color, width=max(1,round(width*S)))


def label(d, xy, value, size, color, bold=False, mono=False):
    d.text((xy[0]*S,xy[1]*S),value,font=font(size,bold,mono),fill=color,anchor="lt")


def circle(d, xy, radius, fill=None, outline=None, width=1):
    x,y=xy
    d.ellipse(((x-radius)*S,(y-radius)*S,(x+radius)*S,(y+radius)*S),
              fill=fill,outline=outline,width=round(width*S))


def dot(a,b):
    return sum(x*y for x,y in zip(a,b))


def project(v):
    return (ORIGIN[0]+SCALE*dot(v,RIGHT), ORIGIN[1]-SCALE*dot(v,UP))


def segments(d, vectors, color, visible=lambda v: True, width=1):
    current=[]
    for v in vectors:
        if visible(v):
            current.append(project(v))
        else:
            line(d,current,color,width)
            current=[]
    line(d,current,color,width)


def dashed(d, points, color, width=1, step=4):
    for i in range(0,len(points)-1,step*2):
        line(d,points[i:i+step+1],color,width)


def earth(d, p, t):
    r=orbit.EARTH_RADIUS_KM
    circle(d,ORIGIN,r*SCALE,p["globe"],p["dim"])
    theta=2*math.pi*t/orbit.SIDEREAL_DAY_S
    for lat in (-60,-30,0,30,60):
        a=math.radians(lat)
        points=[(r*math.cos(a)*math.cos(u/90*math.pi+theta),
                 r*math.cos(a)*math.sin(u/90*math.pi+theta),r*math.sin(a)) for u in range(181)]
        segments(d,points,p["dim"] if lat==0 else p["faint"],lambda v:dot(v,LOOK)>=0)
    for lon in range(0,360,30):
        b=math.radians(lon)+theta
        points=[(r*math.cos(a/180*math.pi)*math.cos(b),
                 r*math.cos(a/180*math.pi)*math.sin(b),r*math.sin(a/180*math.pi)) for a in range(-90,91)]
        segments(d,points,p["faint"],lambda v:dot(v,LOOK)>=0)
    for ring in LAND:
        points=[]
        for lon,lat in ring:
            a,b=math.radians(lat),math.radians(lon)+theta
            points.append((r*math.cos(a)*math.cos(b),r*math.cos(a)*math.sin(b),r*math.sin(a)))
        segments(d,points,p["dim"],lambda v:dot(v,LOOK)>=0,0.7)


def ground_track(d,p,t):
    x0,x1,y0,y1=775,1378,286,510
    def map_point(lon,lat):
        return x0+(lon+180)/360*(x1-x0),y1-(lat+90)/180*(y1-y0)
    for lon in (-180,-120,-60,0,60,120,180):
        x,_=map_point(lon,0)
        line(d,[(x,y0),(x,y1)],p["faint"])
        label(d,(x-15,y1+12),str(lon),14,p["muted"],mono=True)
    for lat in (-90,-55,0,55,90):
        _,y=map_point(0,lat)
        line(d,[(x0,y),(x1,y)],p["dim"] if lat==0 else p["faint"])
        label(d,(x0-46,y-7),f"{lat:+d}" if lat else "0",14,p["muted"],mono=True)
    for ring in LAND:
        path=[]
        last_lon=None
        for lon,lat in ring:
            if last_lon is not None and abs(lon-last_lon)>180:
                line(d,path,p["dim"],0.6)
                path=[]
            path.append(map_point(lon,lat))
            last_lon=lon
        line(d,path,p["dim"],0.6)
    for lap in range(2):
        path=[]
        last_lon=None
        for k in range(601):
            lon,lat=orbit.ground_point((lap+k/600)*orbit.PERIOD_S)
            if last_lon is not None and abs(lon-last_lon)>180:
                line(d,path,p["blue"] if lap==0 else p["dim"],1.8 if lap==0 else 1)
                path=[]
            path.append(map_point(lon,lat))
            last_lon=lon
        line(d,path,p["blue"] if lap==0 else p["dim"],1.8 if lap==0 else 1)
    pt=map_point(*orbit.ground_point(t))
    circle(d,pt,8,outline=p["amber"],width=1)
    circle(d,pt,3,fill=p["amber"])
    label(d,(1218,550),"longitude / deg",14,p["muted"],mono=True)
    label(d,(775,257),"latitude / deg",14,p["muted"],mono=True)


def render(theme,t=0):
    p=PALETTES[theme]
    image=Image.new("RGB",(W*S,H*S),p["bg"])
    d=ImageDraw.Draw(image)
    label(d,(34,28),"EVAN GIRARD-SUN",61,p["ink"],bold=True)
    label(d,(38,112),"Robotics & computer vision",27,p["blue"])
    line(d,[(36,169),(1402,169)],p["faint"])
    label(d,(38,193),"ORBITAL NAVIGATION",18,p["ink"],mono=True)
    label(d,(1045,193),"MEO / REFERENCE GEOMETRY",16,p["muted"],mono=True)
    label(d,(38,238),"01   EARTH-CENTERED ORBIT",16,p["muted"],mono=True)
    label(d,(775,238),"02   EARTH-FIXED GROUND TRACK",16,p["muted"],mono=True)
    vectors=[orbit.position(k*orbit.PERIOD_S/720) for k in range(721)]
    # The equatorial reference is a plane guide, not a second spacecraft orbit.
    eq=[project((orbit.RADIUS_KM*math.cos(k*math.pi/180),orbit.RADIUS_KM*math.sin(k*math.pi/180),0)) for k in range(361)]
    dashed(d,eq,p["faint"])
    segments(d,vectors,p["dim"],lambda v:dot(v,LOOK)<0,1.3)
    earth(d,p,t)
    segments(d,vectors,p["blue"],lambda v:dot(v,LOOK)>=0,1.8)
    v=orbit.position(t)
    pt=project(v)
    nadir=project(tuple(a*orbit.EARTH_RADIUS_KM/orbit.RADIUS_KM for a in v))
    if dot(v,LOOK)>0:
        rays=[(nadir[0]+(pt[0]-nadir[0])*k/24,nadir[1]+(pt[1]-nadir[1])*k/24) for k in range(25)]
        dashed(d,rays,p["amber"],step=2)
    circle(d,pt,7,fill=p["bg"],outline=p["amber"],width=1.4)
    circle(d,pt,2,fill=p["amber"])
    label(d,(ORIGIN[0]-22,ORIGIN[1]+73),"EARTH",13,p["muted"],mono=True)
    ground_track(d,p,t)
    line(d,[(36,588),(1402,588)],p["faint"])
    label(d,(38,615),"h 20,200 km    i 55.0 deg    T %.2f h"%(orbit.PERIOD_S/3600),17,p["muted"],mono=True)
    label(d,(1008,615),"t + %05.2f h  /  2 revolutions"%(t/3600),16,p["amber"],mono=True)
    return image.resize((W,H),Image.Resampling.LANCZOS)


def main():
    for theme in PALETTES:
        frames=[render(theme,k/40*2*orbit.PERIOD_S) for k in range(40)]
        frames[0].save(ROOT/"assets"/f"orbit-{theme}.png",optimize=True)
        frames[0].save(ROOT/"assets"/f"orbit-{theme}.gif",save_all=True,
                       append_images=frames[1:],duration=160,loop=0,optimize=True)
    print("Rendered matching orbit and ground-track views")


if __name__=="__main__":
    main()
