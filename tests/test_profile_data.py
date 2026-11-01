from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from render_profile import CalendarParser, lorenz_trace


class ProfileDataTests(unittest.TestCase):
    def test_counts_come_from_tooltips_and_dates_are_sorted(self):
        p=CalendarParser()
        p.feed('''<td id="b" data-date="2026-01-02" data-level="4"></td>
        <tool-tip for="b">1,234 contributions on January 2nd.</tool-tip>
        <td id="a" data-date="2026-01-01" data-level="0"></td>
        <tool-tip for="a">No contributions on January 1st.</tool-tip>''')
        self.assertEqual([day["count"] for day in p.result()],[0,1234])

    def test_missing_counts_are_not_silently_treated_as_zero(self):
        p=CalendarParser()
        p.feed('<td id="a" data-date="2026-01-01" data-level="0"></td>')
        with self.assertRaises(ValueError):
            p.result()

    def test_changed_tooltip_format_is_rejected(self):
        p=CalendarParser()
        with self.assertRaises(ValueError):
            p.feed('<td id="a" data-date="2026-01-01" data-level="0"></td><tool-tip for="a">Unknown</tool-tip>')

    def test_phase_portrait_is_finite_and_fits_header(self):
        trace=lorenz_trace()
        self.assertGreater(len(trace),5000)
        self.assertTrue(all(750<x<1250 and 25<y<265 for x,y in trace))


if __name__=="__main__":
    unittest.main()
