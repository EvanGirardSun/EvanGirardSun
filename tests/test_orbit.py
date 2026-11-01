from pathlib import Path
import math
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import orbit


class OrbitTests(unittest.TestCase):
    def test_constant_radius_and_periodic_inertial_position(self):
        for k in range(101):
            t=k*orbit.PERIOD_S/100
            self.assertAlmostEqual(math.sqrt(sum(x*x for x in orbit.position(t))),orbit.RADIUS_KM,places=7)
            for a,b in zip(orbit.position(t),orbit.position(t+orbit.PERIOD_S)):
                self.assertAlmostEqual(a,b,places=7)

    def test_inclination_sets_latitude_limits(self):
        self.assertAlmostEqual(orbit.ground_point(orbit.PERIOD_S/4)[1],55)
        self.assertAlmostEqual(orbit.ground_point(3*orbit.PERIOD_S/4)[1],-55)

    def test_earth_rotation_shifts_successive_ground_tracks(self):
        lon,lat=orbit.ground_point(orbit.PERIOD_S)
        expected=-360*orbit.PERIOD_S/orbit.SIDEREAL_DAY_S
        expected=(expected+180)%360-180
        self.assertAlmostEqual(lon,expected,places=8)
        self.assertAlmostEqual(lat,0,places=8)

    def test_meo_reference_period(self):
        self.assertTrue(11.9<orbit.PERIOD_S/3600<12.1)


if __name__=="__main__":
    unittest.main()
