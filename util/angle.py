#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

class Angle:
    """
    Stores an angle in radians. 
    Handles output in a variety of formats: radians, degrees, latitude, longitude, hour angle
    """

    def __init__(self, rad):
        self.__rad = float(rad)

    def rad(self):
        return self.__rad

    def deg(self):
        return math.degrees(self.__rad)

    def lat(self):
        direction = "N" if self.__rad >= 0 else "S"

        deg = math.degrees(abs(self.__rad))
        minutes = deg % 1 * 60
        seconds = minutes % 1 * 60
        return str(int(deg))+"° "+str(int(minutes))+"' "+str(seconds)+"\" "+direction

    def lon(self):
        direction = "E" if self.__rad >= 0 else "W"

        deg = math.degrees(abs(self.__rad))
        minutes = deg % 1 * 60
        seconds = minutes % 1 * 60
        return str(int(deg))+"° "+str(int(minutes))+"' "+str(seconds)+"\" "+direction

    def deg_min_sec(self):
        direction = "" if self.__rad >= 0 else "-"

        deg = math.degrees(abs(self.__rad))
        minutes = deg % 1 * 60
        seconds = minutes % 1 * 60
        return direction+str(int(deg))+"° "+str(int(minutes))+"' "+str(seconds)+"\" "


    def hour(self):
        direction = "" if self.__rad >= 0 else "-"

        hours = abs(self.__rad)/math.pi*12
        minutes = hours % 1 * 60
        seconds = minutes % 1 * 60
        return direction+str(int(hours))+"h "+str(int(minutes))+"m "+str(seconds)+"s"

    def add(self, angle):
        return Angle(self.rad() + angle.rad())

    def sub(self, angle):
        return Angle(self.rad() - angle.rad())

    def __float__(self):
        return self.rad()

    def __str__(self):
        return str(self.rad())

class Degree(Angle):
    """ Allows input in degrees """
    def __init__(self, deg):
        Angle.__init__(self, math.radians(float(deg)))

class Latlon(Angle):
    """ Allows input as lat/lon """
    def __init__(self, d, m, s, direction="N"):
        direction = -1 if direction == "S" or direction == "W" else 1
        direction *= -1 if d < 0 else 1

        Angle.__init__(self, math.radians(abs(d) + m/60.0 + s/3600.0)*direction)

class HourAngle(Angle):
    """ Allows input as hour angle """
    def __init__(self, h, m, s, direction=1):
        direction *= -1 if h < 0 else 1

        Angle.__init__(self, (abs(h) + m/60.0 + s/3600.0)*direction*math.pi/12.0)




"""
For testing only
"""
if __name__ == "__main__":

    def test():
        assert Degree(180).rad() == math.pi
        assert Degree(-180).deg() == -180.0
        assert Degree(256.12).lat() == "256° 7' 12.0\" N"
        assert Degree(-256.12).lon() == "256° 7' 12.0\" W"
        assert Degree(-90).hour() == "-6h 0m 0.0s"
        assert Angle(3.14/2).hour() == "5h 59m 49.0497205294s"

        assert Latlon(90, 30, 30, 'N').lat() == "90° 30' 30.0\" N"
        assert Latlon(-90, 30, 30, 'N').lat() == "90° 30' 30.0\" S"
        assert Latlon(90, 30, 30, 'W').lon() == "90° 30' 30.0\" W"
        assert Latlon(-45, 0, 30, 'E').lon() == "45° 0' 30.0\" W"

        assert HourAngle(4, 30, 30).hour() == "4h 30m 30.0s"
        assert HourAngle(-12, 30, 30).hour() == "-12h 30m 30.0s"
        assert HourAngle(18, 30, 30).hour() == "18h 30m 30.0s"
        assert HourAngle(-6, 30, 30, -1).hour() == "6h 30m 30.0s"

    test()
