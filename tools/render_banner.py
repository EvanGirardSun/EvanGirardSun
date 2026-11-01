"""Draw a blinking workbench robot and the profile header without external assets."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def font(size, bold=False):
    paths = (["C:/Windows/Fonts/segoeuib.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if bold
             else ["C:/Windows/Fonts/segoeui.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"])
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def draw_frame(dark, tick=0, blink=False):
    bg, ink, muted, grid = (("#101b20", "#edf3e8", "#a3b6b6", "#24353a") if dark else
                           ("#f4f5ed", "#152d33", "#53696c", "#dbe4da"))
    mint, orange = "#94cfb0", "#e9a057"
    image = Image.new("RGB", (1280, 320), bg)
    d = ImageDraw.Draw(image)
    for x in range(800, 1280, 24):
        for y in range(20, 320, 24):
            d.ellipse((x, y, x+1, y+1), fill=grid)
    d.text((48, 32), "EVAN / ENGINEERING", font=font(16, True), fill=muted)
    d.text((43, 78), "Evan Girard–Sun", font=font(66, True), fill=ink)
    d.text((48, 178), "Robotics & embedded systems", font=font(29), fill=muted)
    d.rounded_rectangle((48, 255, 61, 268), radius=4, fill=mint)
    d.text((76, 247), "Rice University  /  Phi Lab", font=font(21), fill=ink)
    x, y = 1040, 142 + round(4 * math.sin(tick * math.pi / 4))
    d.ellipse((933, 281, 1147, 292), fill=grid)
    d.line((x, y-58, x, y-88), fill=ink, width=5)
    d.ellipse((x-7, y-99, x+7, y-85), fill=orange)
    d.rounded_rectangle((x-83, y-55, x+83, y+43), radius=24, fill=mint)
    d.rounded_rectangle((x-61, y-34, x+61, y+20), radius=15, fill="#193c40")
    for eye in (x-29, x+29):
        if blink:
            d.line((eye-10, y-4, eye+10, y-4), fill="#e7f5d8", width=5)
        else:
            d.rounded_rectangle((eye-7, y-18, eye+7, y+2), radius=6, fill="#e7f5d8")
    d.arc((x-11, y-1, x+11, y+12), 0, 180, fill="#e7f5d8", width=3)
    d.rounded_rectangle((x-43, y+49, x+43, y+112), radius=12, fill=mint)
    d.rounded_rectangle((x-24, y+65, x+24, y+89), radius=6, fill="#193c40")
    for dot, color in ((-12, orange), (0, mint), (12, "#e7f5d8")):
        d.ellipse((x+dot-3, y+73, x+dot+3, y+79), fill=color)
    d.line((x-45, y+64, x-76, y+92), fill=mint, width=12)
    d.line((x+45, y+64, x+77, y+42, x+93, y+16), fill=mint, width=12)
    d.ellipse((x+84, y+3, x+104, y+23), fill=orange)
    for foot in (-25, 25):
        d.rounded_rectangle((x+foot-17, y+108, x+foot+17, y+123), radius=5, fill=ink)
    return image


def main():
    for theme in ("dark", "light"):
        frames = [draw_frame(theme == "dark", tick, blink=tick == 5) for tick in range(8)]
        assert all(f.size == (1280, 320) for f in frames)
        assert frames[0].tobytes() != frames[5].tobytes()
        frames[0].save(ROOT / "assets" / f"workbench-{theme}.png", optimize=True)
        frames[0].save(ROOT / "assets" / f"workbench-{theme}.gif", save_all=True,
                       append_images=frames[1:], duration=[1800, 180, 180, 180, 180, 110, 180, 180], loop=0)
        draw_pipeline(theme == "dark").save(ROOT / "assets" / f"control-loop-{theme}.png", optimize=True)
    draw_avatar().save(ROOT / "assets" / "robot-avatar.png", optimize=True)
    print("Built robot banners, control-loop strips and a matching avatar")


def draw_pipeline(dark):
    bg, ink, muted = ("#101b20", "#edf3e8", "#a3b6b6") if dark else ("#f4f5ed", "#152d33", "#53696c")
    image = Image.new("RGB", (1280, 156), bg)
    d = ImageDraw.Draw(image)
    labels = [("CAMERA", "analog video"), ("POSE", "AprilTags"),
              ("CONTROL", "mission + PD/I"), ("RADIO", "CRSF / ELRS")]
    for i, (title, detail) in enumerate(labels):
        x = 44 + i * 316
        d.text((x, 28), f"0{i+1}", font=font(17, True), fill="#94cfb0" if dark else "#347859")
        d.text((x, 60), title, font=font(27, True), fill=ink)
        d.text((x, 104), detail, font=font(21), fill=muted)
        if i < 3:
            d.line((x+223, 76, x+265, 76), fill=muted, width=2)
            d.line((x+257, 69, x+265, 76, x+257, 83), fill=muted, width=2)
    return image


def draw_avatar():
    image = Image.new("RGB", (500, 500), "#101b20")
    d = ImageDraw.Draw(image)
    # Keep the face and antenna inside GitHub's circular avatar crop.
    d.ellipse((32, 32, 468, 468), fill="#172c30")
    d.line((250, 170, 250, 115), fill="#94cfb0", width=10)
    d.ellipse((235, 91, 265, 121), fill="#e9a057")
    d.rounded_rectangle((82, 165, 418, 365), radius=48, fill="#94cfb0")
    d.rounded_rectangle((123, 207, 377, 317), radius=30, fill="#193c40")
    for x in (190, 310):
        d.rounded_rectangle((x-14, 235, x+14, 277), radius=12, fill="#e7f5d8")
    d.arc((228, 267, 272, 296), 0, 180, fill="#e7f5d8", width=6)
    d.rounded_rectangle((214, 377, 286, 401), radius=8, fill="#94cfb0")
    return image


if __name__ == "__main__":
    main()
