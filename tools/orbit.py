"""Circular two-body MEO reference with a spherical, uniformly rotating Earth.

Geometry only: no ephemeris, perturbations or operational navigation solution.
Reference: https://www.faa.gov/about/office_org/headquarters_offices/ato/service_units/techops/navservices/gnss/gps/spacesegments
"""
import math

EARTH_RADIUS_KM = 6378.137
MU_KM3_S2 = 398600.4418
SIDEREAL_DAY_S = 86164.0905
ALTITUDE_KM = 20200.0
INCLINATION_DEG = 55.0
RADIUS_KM = EARTH_RADIUS_KM + ALTITUDE_KM
PERIOD_S = 2 * math.pi * math.sqrt(RADIUS_KM**3 / MU_KM3_S2)


def position(t):
    u = 2 * math.pi * t / PERIOD_S
    inclination = math.radians(INCLINATION_DEG)
    return (RADIUS_KM * math.cos(u),
            RADIUS_KM * math.sin(u) * math.cos(inclination),
            RADIUS_KM * math.sin(u) * math.sin(inclination))


def ground_point(t):
    x, y, z = position(t)
    theta = 2 * math.pi * t / SIDEREAL_DAY_S
    xe = math.cos(theta)*x + math.sin(theta)*y
    ye = -math.sin(theta)*x + math.cos(theta)*y
    latitude = math.degrees(math.asin(z / RADIUS_KM))
    longitude = math.degrees(math.atan2(ye, xe))
    return longitude, latitude
