"""Render a photograph as actual ASCII characters, with optional edge strokes."""
import argparse
import html
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

RAMP = " .,:;=+*#%@"


def ascii_rows(image, columns=100, aspect=0.48):
    if not 16 <= columns <= 240 or not 0.25 <= aspect <= 1:
        raise ValueError("Use 16–240 columns and a character aspect between 0.25 and 1")
    gray = ImageOps.autocontrast(ImageOps.grayscale(image), cutoff=1)
    rows = max(1, round(gray.height / gray.width * columns * aspect))
    gray = gray.resize((columns, rows), Image.Resampling.LANCZOS)
    pixels = gray.load()
    output = []
    for y in range(rows):
        line = []
        for x in range(columns):
            value = pixels[x, y]
            char = RAMP[round((255 - value) / 255 * (len(RAMP) - 1))]
            if 0 < x < columns - 1 and 0 < y < rows - 1:
                dx = pixels[x + 1, y] - pixels[x - 1, y]
                dy = pixels[x, y + 1] - pixels[x, y - 1]
                if abs(dx) + abs(dy) > 115:
                    if abs(dx) > 2 * abs(dy):
                        char = "|"
                    elif abs(dy) > 2 * abs(dx):
                        char = "-"
                    else:
                        char = "/" if dx * dy > 0 else "\\"
            line.append(char)
        output.append("".join(line))
    return output


def mono_font(path=None, size=14):
    candidates = [path] if path else [
        "C:/Windows/Fonts/consola.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/System/Library/Fonts/Menlo.ttc",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return ImageFont.truetype(str(candidate), size)
    raise ValueError("Supply --font with a local monospace TTF or OTF")


def render(rows, font, foreground="#e8e2d7", background="#101211"):
    cell = max(1, round(font.getlength("M")))
    line = max(1, round(font.size * 1.12))
    image = Image.new("RGB", (cell * len(rows[0]) + 32, line * len(rows) + 32), background)
    draw = ImageDraw.Draw(image)
    for y, row in enumerate(rows):
        draw.text((16, 16 + y * line), row, fill=foreground, font=font, anchor="lt")
    return image


def svg(rows, foreground="#e8e2d7", background="#101211"):
    width, height = len(rows[0]) * 9 + 32, len(rows) * 16 + 32
    lines = "\n".join(
        f'<text x="16" y="{28 + y * 16}" xml:space="preserve">{html.escape(row)}</text>'
        for y, row in enumerate(rows)
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Portrait rendered from ASCII characters">
<rect width="100%" height="100%" fill="{background}"/>
<g fill="{foreground}" font-family="monospace" font-size="15">{lines}</g>
</svg>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, default=Path("portrait"), help="Output stem; writes .txt, .svg and .png")
    parser.add_argument("--columns", type=int, default=100)
    parser.add_argument("--font", type=Path)
    parser.add_argument("--light", action="store_true")
    args = parser.parse_args()
    colors = ("#202724", "#ffffff") if args.light else ("#e8e2d7", "#101211")
    with Image.open(args.image) as image:
        rows = ascii_rows(ImageOps.exif_transpose(image), args.columns)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.with_suffix(".txt").write_text("\n".join(rows) + "\n", encoding="utf-8")
    args.output.with_suffix(".svg").write_text(svg(rows, *colors), encoding="utf-8")
    render(rows, mono_font(args.font), *colors).save(args.output.with_suffix(".png"))
    print(f"Wrote {args.output}.txt / .svg / .png ({len(rows[0])} × {len(rows)} characters)")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
