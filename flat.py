#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util.angle import *
from util.vector3 import Vector3
from util.location import SphereLocation, StarLocation

import math

METERS_PER_RADIAN_LAT = 40008000.0 / 2 / math.pi 


class Location(SphereLocation):
    """
    Maps spherical lat/lon coordinates to a disk by converting latitude to a radial distance.
    """
    def __init__(self, lat, lon):
        SphereLocation.__init__(self, lat, lon)
        self.radius = float(lat) * METERS_PER_RADIAN_LAT

    def vector(self):
        """
        Location represented by vector. 

        GMT points along Y axis
        North pole points along Z axis

        """
        x = self.radius * math.sin(-1*self.lon.rad())
        y = self.radius * math.cos(self.lon.rad())
        return Vector3(x,y,0)


class Star(StarLocation):
    def __init__(self, ra, dec):
        """
        Provides methods to calculate the azimuth and altitude of stars based on the guide particle method for a flat earth.

        :param ra: Right Ascension
        :param dec: Declination
        """
        self.ra = ra
        self.dec = dec

    def base_ray_direction(self):
        """
        Right Ascension and Declination represented by a vector. 

        Vernal Equinox points along Y axis. 
        North pole points along Z axis.
        """
        direction = Vector3(0,1,0) # starts pointing towards the Y axis and vernal equinox
        direction.rotateX(self.dec.rad()) # declination rotation around X axis
        direction.rotateZ(self.ra.rad()) # right ascension rotation around Z axis

        return direction

    def local_ray_direction(self, location, gmst):
        """
        Rotates the base vector according to the locations latitude/longitude and sidereal time.

        :param location: Location containing lat/lon coordinates
        :param gmst: Angle containing Greenwich Mean Sidereal Time
        """
        direction = self.base_ray_direction() # get base vector
        lst = self.local_sidereal_time(location, gmst).rad() # calculate sidereal time for given location

        direction.rotateZ(-lst) # rotate to align the longitude with the Y axis to allow easy rotation
        direction.rotateX(math.pi/2.0 - location.lat.rad()) # rotate around X axis, towards north pole based on latitude
        direction.rotateZ(lst) # undo previous rotation to unalign with Y axis

        return direction

    def local_sidereal_time(self, location, gmst):
        'Sidreal time for given location. Angle of location relative to vernal equinox.'
        return Angle(gmst.rad() + location.lon.rad())

    def altitude(self, location, gmst):
        """
        Calculates the apparent altitude of the star based on the direction of the guide vector. 

        :param location: Location containing lat/lon coordinates
        :param gmst: Angle containing Greenwich Mean Sidereal Time
        """
        direction = self.local_ray_direction(location, gmst) # guide vector

        return Angle(math.asin(direction.z / direction.length()))

    def azimuth(self, location, gmst):
        """
        Calculates the apparent azimuth of the star based on the direction of the guide vector. 

        :param location: Location containing lat/lon coordinates
        :param gmst: Angle containing Greenwich Mean Sidereal Time
        """
        direction = self.local_ray_direction(location, gmst) # guide vector

        absolute_direction = 0

        # avoid divide-by-zero errors
        if direction.x == 0:
            if direction.y > 0:
                absolute_direction = math.pi/2
            else:
                absolute_direction = -math.pi/2
        else:
            # calculate direction relative to global coordinate system
            absolute_direction = math.atan(direction.y/direction.x) 

        # arctan() range is limited to -90 to 90 degrees. To detect 90 to 270 degrees, test sign of x component.
        if direction.x < 0:
            absolute_direction += math.pi

        # adjust angle relative to direction of North Pole. Towards North Pole should be zero degrees.
        azimuth = gmst.rad() + location.lon.rad() - math.pi/2 - absolute_direction 

        # normalize azimuth to range of 0 to 360 degrees
        if azimuth < 0:
            azimuth -= int(azimuth/math.pi/2.0 - 1)*math.pi*2.0
        if azimuth >= math.pi*2: 
            azimuth -= int(azimuth/math.pi/2.0)*math.pi*2.0

        return Angle(azimuth)

    def sphere_intercept(self, location, gmst, sphere_radius):

        """
        Raycast the star's light until it intersects with the celestial sphere at the given radius R.

        x^2 + y^2 + z^2 = R^2
        x = x_offset + x_direction*t
        y = y_offset + y_direction*t
        z = z_offset + z_direction*t

        1. Solve for t by combining above equations into a single quadratic equation.
        2. Plug in t to solve for the x, y, and z coordinates on the celestial sphere.

        """

        d = self.local_ray_direction(location, gmst) # unit vector representing direction of starlight ray (d for direction)
        o = location.vector() # vector representing terestial origin of starlight ray (o for offset)

        # solve quadratic equation a*t^2 + b*t + c = 0
        a = d.x*d.x + d.y*d.y + d.z*d.z
        b = 2*(o.x*d.x + o.y*d.y + o.z*d.z)
        c = o.x*o.x + o.y*o.y + o.z*o.z - sphere_radius*sphere_radius

        sqrt = 0

        try:
            sqrt = math.sqrt(b*b - 4*a*c)
        except ValueError:
            print("Invalid Celestial sphere radius: "+str(sphere_radius)+". Should be in meters and greater than 40,008,000 meters.")
            raise 

        # apply the quadratic formula
        # make sure we have the positive solution only.
        t = (-1*b + sqrt)/(2*a)
        if t < 0:
            t = (-1*b - sqrt)/(2*a)

        # plug t back into the parameterized starlight ray to get intercept coordinates on the celestial sphere
        x = o.x + d.x*t
        y = o.y + d.y*t
        z = o.z + d.z*t

        return Vector3(x,y,z)
        


if __name__ == "__main__":

    def test():
        star = Star(Angle(6.0), Angle(math.pi/2.0))
        location = Location(Angle(math.pi/4.0), Angle(math.pi/2.0))
        gmst = HourAngle(4,0,0) 
        print(star.base_ray_direction())
        print(star.local_ray_direction(location, gmst))
        print(star.azimuth(location, gmst).deg_min_sec())
        print(star.altitude(location, gmst).deg_min_sec())

        print("------")
        gmst = HourAngle(4,0,0) 
        print(star.azimuth(location, gmst).deg_min_sec())
        gmst = HourAngle(0,0,0) 
        print(star.azimuth(location, gmst).deg_min_sec())
        gmst = HourAngle(-6,0,0) 
        print(star.azimuth(location, gmst).deg_min_sec())
        gmst = HourAngle(-21,0,0) 
        print(star.azimuth(location, gmst).deg_min_sec())
        gmst = HourAngle(60,30,0) 
        print(star.azimuth(location, gmst).deg_min_sec())
        gmst = HourAngle(-41,0,0) 
        print(star.azimuth(location, gmst).deg_min_sec())

    test()
