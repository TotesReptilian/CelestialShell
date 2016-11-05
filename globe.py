#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import math

from util.angle import Angle, Degree, Latlon, HourAngle
from util.location import StarLocation, SphereLocation
from util.vector3 import Vector3

class Star(StarLocation):
    def __init__(self, ra, dec):
        """
        :param ra: Latlon Right Ascension
        :param dec: HourAngle Declination
        """
        StarLocation.__init__(self, ra, dec)

    def azimuth(self, location, gmst):
        """
        Calculates azimuth angle of this star from given location

        :param location: Location
        :param gmst: HourAngle greenwich sidereal time

        :return: azimuth Angle
        """
        lha = self.local_hour_angle(location, gmst)

        den = math.sin(location.lat) * math.cos(lha) - math.tan(self.dec)*math.cos(location.lat)
        sin_lha = math.sin(lha)

        # prevent divide-by-zero error
        if den == 0:
            if sin_lha == 0:
                return Angle(0)
            elif sin_lha > 0:
                return Angle(math.pi*1.5)
            else:
                return Angle(math.pi*0.5)

        atan = math.atan(sin_lha / den)

        # atan range is from -90 to 90. Must manually detect other quandrants from sign of denomenator
        if den > 0:
            atan += math.pi

        # enforce 0 - 360 range.
        if atan < 0:
            atan += math.pi*2.0

        return Angle(atan)

    def altitude(self, location, gmst):
        """
        Calculates altitude angle of this star from given location

        :param location: Location
        :param gmst: greenwich sidereal time

        :return: altitude Angle
        """
        lha = self.local_hour_angle(location, gmst)
        return Angle(math.asin(math.sin(location.lat)*math.sin(self.dec) + math.cos(location.lat)*math.cos(self.dec)*math.cos(lha)))

    def local_hour_angle(self, location, gmst):
        """
        Calculates local hour angle of this star from given location

        :param location: Location
        :param gmst: greenwich sidereal time

        :return: local hour angle
        """

        return Angle(gmst.rad() + location.lon.rad() - self.ra.rad())

    def greenwich_hour_angle(self, location, gmst):
        """
        Calculates greenwich hour angle of this star from given location

        :param location: Location
        :param gmst: greenwich sidereal time

        :return: local hour angle
        """
        return Angle(gmst.rad() - self.ra)

    def local_sidereal_time(self, location, gmst):
        return Angle(gmst.rad() + location.lon.rad())


    def print_azi_alt(self, loc, gmst):
        print("Azi: "+self.azimuth(loc, gmst).deg_min_sec())
        print("Alt: "+self.altitude(loc, gmst).deg_min_sec())


