#!/usr/bin/env python
# -*- coding: utf-8 -*-

import flat
import globe

from util.angle import Angle, Degree, Latlon, HourAngle
from util.vector3 import Vector3
from util.location import SphereLocation, StarLocation
from util.gmst import utc, gmst

import csv
import cmd
from datetime import datetime

DEFAULT_GMST = gmst(datetime.now(utc))
DEFAULT_CELESTIAL_SPHERE_RADIUS = 400080000 # meters (default is ten times bigger than earth radius)


class App(cmd.Cmd):

    intro = "Compare location of stars in flat model with globe model. Type <help> or <?> to list commands. Type <go> to run comparison.\n"

    doc_header =  "Commands (type help <topic>)"
    ruler = "-"

    prompt = "> "

    def __init__(self):
        cmd.Cmd.__init__(self)

        self.stars = get_location_data('data/stars.csv', HourAngle, Latlon, StarLocation)
        self.locations = get_location_data('data/locations.csv', Latlon, Latlon, SphereLocation)

        self.selected_stars = self.stars
        self.selected_locations = self.locations
        self.gmst = DEFAULT_GMST
        self.verbose = False
        self.celestial_sphere_radius = DEFAULT_CELESTIAL_SPHERE_RADIUS

    def do_go(self, arg):
        'Run the comparison of selected stars and locations.'

        print("GMST: "+self.gmst.hour()+"\n")

        for name, location in self.selected_locations.items():
            print(name+":")
            if self.verbose:
                print("Lat/Lon: "+location.lat.lat()+"/"+location.lon.lon())
            for name, star in self.selected_stars.items():
                globe_star = globe.Star(star.ra, star.dec)
                flat_star = flat.Star(star.ra, star.dec)
                flat_location = flat.Location(location.lat, location.lon)
                print("\t"+name+":")
                if self.verbose:
                    print("\tRA/Dec: "+globe_star.ra.hour()+"/"+globe_star.dec.deg_min_sec())
                    print("\tLocal Hour Angle: "+globe_star.local_hour_angle(location, self.gmst).hour())
                    print("\tLocal Sidereal Time: "+globe_star.local_sidereal_time(location, self.gmst).hour())
                print("\t\tglobe: Az/Alt: "+globe_star.azimuth(location, self.gmst).deg_min_sec()+"/"+globe_star.altitude(location, self.gmst).deg_min_sec())
                print("\t\tflat:  Az/Alt: "+flat_star.azimuth(flat_location, self.gmst).deg_min_sec()+"/"+flat_star.altitude(flat_location, self.gmst).deg_min_sec())
                if self.verbose:
                    print("\t\t\tBase Ray Direction:  "+str(flat_star.base_ray_direction()))
                    print("\t\t\tLocal Ray Direction: "+str(flat_star.local_ray_direction(location, self.gmst)))
                    print("\t\t\tCelstial Sphere Intersept: "+str(flat_star.sphere_intercept(flat_location, self.gmst, self.celestial_sphere_radius)))

            print("\n")

    def do_star(self, arg):
        'Select stars for output. Example: star nu_oct sirius polaris'

        if arg:
            selected = {key: self.stars[key] for key in arg.split() if key in self.stars.keys()}

            if len(selected) < 1:
                print("No valid stars given.")
                self.list_stars()
            else:
                self.selected_stars = selected

        print("Selected stars: "+", ".join(self.selected_stars.keys()))

    def complete_star(self, text, line, begidx, endidx):
        return [i for i in self.stars.keys() if i.startswith(text)]

    def do_location(self, arg):
        'Select locations for output. Example: location perth rio'

        if arg:
            selected = {key: self.locations[key] for key in arg.split()}

            if len(selected) < 1:
                print("No valid locations given. Type \"list\" to see available locations.")
                return

            self.selected_locations = selected

        print("Selected locations: "+", ".join(self.selected_locations.keys())+"")

    def complete_location(self, text, line, begidx, endidx):
        return [i for i in self.locations.keys() if i.startswith(text)]

    def do_radius(self, arg):
        'Radius of the celestial sphere. Must be number greater than 40,008,000 meters'
        if arg:
            try:
                arg = float(arg)
                if arg < 40008000:
                    raise ValueError("Celestial Sphere Radius must be greater than 40,008,000 meters")
            except (TypeError, ValueError):
                print("Invalid radius entered. Radius must be greater than 40,008,000 meters")
            else:
                self.celestial_sphere_radius = arg


        print("Radius of Celestial Sphere: "+str(self.celestial_sphere_radius))



    def do_time(self, arg):
        """
        Set time in UTC timezone. Automatically sets GMST based on given time in UTC timezone. Specifying 'now' sets time to current UTC time.

        Format: time year month day hours minutes seconds

        Example: time 2016 5 5 12 30 0
        Example: time now 

        """
        if arg:
            if arg == "now":
                dt = datetime.now(utc)
            else:
                try:
                    args = tuple(map(int, arg.split()))
                    dt = datetime(*args, tzinfo=utc)
                except (ValueError, IndexError, TypeError):
                    print("Invalid time entered. Please enter in format: year month day hours minutes seconds")
                    return

            self.gmst = gmst(dt)
            print("Set GMST from time: "+dt.strftime("%c %Z"))

        print("GMST: "+self.gmst.hour())


    def do_gmst(self, arg):
        """
        Set Greenwich Mean Sidereal Time. Optionally, use the date command to automatically set GMST.

        Format: gmst hours minutes seconds
        Example: gmst 12 30 30
        """
        if arg:
            try:
                args = tuple(map(float, arg.split()))
                self.gmst = HourAngle(args[0], args[1], args[2])
            except (ValueError, IndexError):
                print("Invalid GMST entered. Please enter in format: hours minutes seconds")

        print("GMST: "+self.gmst.hour())

    def do_verbose(self, arg):
        ' Display extra details. Example: verbose on/off'
        if arg:
            if arg == "off" or arg == "0" or arg == "no":
                self.verbose = False
            else:
                self.verbose = True

        print("Verbose: "+"on" if self.verbose else "off")


    def list_stars(self):
        print("Available stars: "+" ".join(self.stars.keys()))

    def list_locations(self):
        print("Available locations: "+" ".join(self.locations.keys()))

    def do_list(self, arg):
        'List available stars/locations.'
        if arg == "stars":
            self.list_stars()
        elif arg == "locations":
            self.list_locations()
        else:
            self.list_stars()
            self.list_locations()

    def default(self, line):
        print("Invalid command: "+line)
        self.do_help("")

    def emptyline(self):
        #self.do_go("")
        pass

    def do_quit(self, arg):
        "Goodbye."
        return True

    def do_exit(self, arg):
        "Goodbye."
        return True




def get_location_data(filename, angleClass1=Latlon, angleClass2=Latlon, locationClass=SphereLocation):

    data = {}

    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter=',', quotechar='"')
        i = 0
        for row in reader:
            if len(row) == 0 or row[0][:1] == '#':
                continue
            if len(row) == 3:
                data[row[0]] = locationClass(Degree(row[1]), Degree(row[2]))
            elif len(row) == 7:
                args = tuple(map(float, row[1:]))
                data[row[0]] = locationClass(
                        angleClass1(*args[0:3]), 
                        angleClass2(*args[3:6])
                )
            else:
                continue

    return data


if __name__ == '__main__':
    App().cmdloop()

