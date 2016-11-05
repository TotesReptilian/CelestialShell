#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

class Vector3:

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def length(self):
        return math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)

    def norm(self):
        length = self.length()
        self.x /= length
        self.y /= length
        self.z /= length
        return self

    def rotateX(self, angle):
        cos = math.cos(angle)
        sin = math.sin(angle)
        y = self.y
        z = self.z
        self.y = y*cos - z*sin
        self.z = z*cos + y*sin
        return self

    def rotateY(self, angle):
        cos = math.cos(angle)
        sin = math.sin(angle)
        z = self.z
        x = self.x
        self.z = z*cos - x*sin
        self.x = x*cos + z*sin
        return self

    def rotateZ(self, angle):
        cos = math.cos(angle)
        sin = math.sin(angle)
        x = self.x
        y = self.y
        self.x = x*cos - y*sin
        self.y = y*cos + x*sin
        return self

    def add(self, other):
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def multiply(self, scale):
        self.x *= scale
        self.y *= scale
        self.z *= scale
        return self

    def clone(self):
        return Vector3(self.x, self.y, self.z)

    def __str__(self):
        return "<"+str(self.x)+","+str(self.y)+","+str(self.z)+">"



"""
For testing only
"""
if __name__ == "__main__":

    def test():
        v = Vector3(3,4,0)
        assert v.length() == 5.0

        v.rotateX(math.pi/2)
        assert v.length() == 5.0
        assert v.z == 4.0

        v.norm()
        assert v.length() == 1.0

        v.rotateX(0)
        v.rotateY(-5)
        v.rotateZ(1.3)
        assert v.length() == 1.0

        v.multiply(-3)
        assert v.length() == 3.0

        v.add(v)
        assert v.length() == 6.0

        v2 = v.clone()
        v2.multiply(0.5)
        assert v2.length() == 3.0
        assert v.length() == 6.0

    test()
