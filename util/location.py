#!/usr/bin/env python
# -*- coding: utf-8 -*-

class SphereLocation:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

class StarLocation(SphereLocation):
    def __init__(self, ra, dec):
        self.ra = ra
        self.dec = dec
        SphereLocation.__init__(self, ra, dec)

