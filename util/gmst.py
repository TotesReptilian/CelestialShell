#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .angle import Angle 

import math
from datetime import datetime, tzinfo, timedelta

def gmst(dt):
    # timedelta since 2000/1/1 12:00:00 UTC
    delta = dt - start_date
    days = delta.days + delta.seconds/(3600.0*24) + delta.microseconds/(3600.0*24*1000000)

    # approximation for GMST based on elapsed days
    gmst = 18.697374558 + 24.06570982441908*days

    # normalize to range of 0 to 24 hours
    gmst -= int(gmst/24.0) * 24.0

    return Angle(gmst/12.0*math.pi)


ZERO = timedelta(0)
class UTC(tzinfo):
    def utcoffset(self, dt):
        return ZERO
    def tzname(self, dt):
        return "UTC"
    def dst(self, dt):
        return ZERO

utc = UTC()
start_date = datetime(2000, 1, 1, 12, 0, 0, 0, utc)



if __name__ == "__main__":
    
    def test():
        print(gmst(datetime.now(utc)).hour())

    test()
