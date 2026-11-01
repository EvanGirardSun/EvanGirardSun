import sys
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from portrait import ascii_rows, svg


class PortraitTests(unittest.TestCase):
    def test_uniform_images_map_to_correct_density(self):
        self.assertEqual(set("".join(ascii_rows(Image.new("L", (80, 80), 255), 40))), {" "})
        self.assertEqual(set("".join(ascii_rows(Image.new("L", (80, 80), 0), 40))), {"@"})

    def test_aspect_and_svg_escaping(self):
        rows = ascii_rows(Image.new("L", (80, 160), 128), 40)
        self.assertEqual((len(rows[0]), len(rows)), (40, 38))
        root = ET.fromstring(svg(["<> & /\\"]))
        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
        self.assertIn("<> & /\\", "".join(root.itertext()))

    def test_invalid_resolution(self):
        with self.assertRaises(ValueError):
            ascii_rows(Image.new("L", (10, 10)), 1000)


if __name__ == "__main__":
    unittest.main()
