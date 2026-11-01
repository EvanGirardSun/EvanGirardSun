"""Build the profile banner from the character portrait; no network services."""
from pathlib import Path
from html import escape
import argparse
from PIL import Image, ImageDraw, ImageFont
from portrait import ascii_rows, mono_font

ROOT = Path(__file__).resolve().parents[1]


def sans_font(size):
    for name in ("C:/Windows/Fonts/segoeui.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/System/Library/Fonts/Helvetica.ttc"):
        if Path(name).is_file():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default(size=size)


def build(theme, rows):
    dark = theme == "dark"
    bg, fg, muted, accent = ("#0d1117", "#e6e9e5", "#9da9a7", "#dfa476") if dark else ("#ffffff", "#202925", "#626f69", "#99522e")
    font = mono_font(size=11)
    image = Image.new("RGB", (1280, 620), bg)
    draw = ImageDraw.Draw(image)
    draw.line((604, 52, 604, 565), fill="#303834" if dark else "#dce4df", width=1)
    for y, row in enumerate(rows):
        draw.text((38, 23 + y * 12), row, font=font, fill=fg, anchor="lt")
    texts = [(650, 101, "EVAN", 72, fg), (650, 179, "GIRARD–SUN", 67, fg),
             (654, 306, "Engineering at Rice University", 24, muted),
             (654, 347, "Robotics / embedded hardware", 24, muted),
             (654, 476, "evangirardsun.com  ↗", 26, accent)]
    for x, y, text, size, color in texts:
        draw.text((x, y), text, font=sans_font(size), fill=color, anchor="lt")
    draw.text((654, 55), "~/EVANGIRARDSUN", font=mono_font(size=15), fill=accent, anchor="lt")
    image.save(ROOT / "assets" / f"header-{theme}.png", optimize=True)
    lines = "\n".join(f'<text x="38" y="{32 + y * 12}" xml:space="preserve">{escape(row)}</text>' for y, row in enumerate(rows))
    labels = "\n".join(f'<text x="{x}" y="{y + size}" font-size="{size}" fill="{color}">{escape(text)}</text>' for x, y, text, size, color in texts)
    vector = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 620" width="1280" height="620" role="img" aria-label="ASCII portrait of Evan Girard-Sun, engineering at Rice University">
<rect width="1280" height="620" fill="{bg}"/>
<path d="M604 52V565" stroke="{'#303834' if dark else '#dce4df'}"/>
<g fill="{fg}" font-family="Consolas,monospace" font-size="11">{lines}</g>
<g font-family="Segoe UI,Arial,sans-serif">{labels}</g>
<text x="654" y="70" fill="{accent}" font-family="monospace" font-size="15">~/EVANGIRARDSUN</text>
</svg>'''
    (ROOT / "assets" / f"header-{theme}.svg").write_text(vector, encoding="utf-8")
    return image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--animate", action="store_true", help="Also write a subtle character-scan GIF")
    args = parser.parse_args()
    with Image.open(ROOT / "assets" / "portrait-source.png") as source:
        rows = ascii_rows(source, columns=90)
    (ROOT / "assets" / "portrait.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")
    for theme in ("dark", "light"):
        full = build(theme, rows)
        if args.animate:
            frames = [full.quantize(colors=64)]
            accent = "#dfa476" if theme == "dark" else "#99522e"
            for row in range(0, len(rows), 4):
                frame = full.copy()
                ImageDraw.Draw(frame).text((38, 23 + row * 12), rows[row], font=mono_font(size=11), fill=accent, anchor="lt")
                frames.append(frame.quantize(colors=64))
            frames.append(full.quantize(colors=64))
            frames[0].save(ROOT / "assets" / f"header-{theme}.gif", save_all=True,
                           append_images=frames[1:], duration=[800] + [90] * (len(frames) - 2) + [6500], loop=0, optimize=True)
    print("Built dark/light profile headers")


if __name__ == "__main__":
    main()
