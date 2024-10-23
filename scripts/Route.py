"""
    Build route with geospatial coordinates (waypoints), 
    each coordinate describes a trackpoint between waypoints, 
    depending on the speed of a hypothetical drone. 
"""

from math import radians, sin, cos, acos
import logging

SPEED = 160 # km/hr (police drone)
INTERVAL = 2 # sampling interval in seconds
MPSEC = SPEED * 1000 / 60 / 60 # meters/sec
INTERVALLDISTANCE = MPSEC * INTERVAL

class Route:

    def __init__(self, boundingBox):
        """ 
        Initialize the Routes class 
        """
        self.bb = boundingBox # dictionary with top, bottom, left, right
        pass


    def inScope(self, place: tuple):
        """
        check if place tuple (lat,long) is inside the scope of the bounding box (self.bb)
            True:   OK, inside bounding box
            False:  outside of scope 
        """
        # check latitude
        rslt = (place[0] <= self.bb["top"]) and (place[0] >= self.bb["bottom"])
        # check longitude
        rslt = rslt and (place[1] >= self.bb["left"]) and (place[1] <= self.bb["right"]) 
        return rslt


    def calc_distance(self, fromPlace: tuple, toPlace: tuple):
        """
        Calculate the distance (in meters) between two points on the globe (haversine formula)
        """
        mlat = radians(fromPlace[0])
        mlon = radians(fromPlace[1])
        plat = radians(toPlace[0])
        plon = radians(toPlace[1])
        dist = 6371.01 * acos(sin(mlat)*sin(plat) + cos(mlat)*cos(plat)*cos(mlon - plon))
        return int(dist*1000) # distance in meters


    def build_tracks(self, fromWP: tuple, toWP: tuple):
        """
        Build the trackpoints from one waypoint, to another waypoint, 
        in 'steps', each defined by a (lat, long) tuple.
        'steps' are defined like flying with a hypothetical drone.
        """
        if self.inScope(fromWP): 
            if self.inScope(toWP):
                distance = self.calc_distance(fromWP, toWP)
                steps = int(distance / INTERVALLDISTANCE)
                # build tracks
                track = [None]*steps # mutable
                track[0] = fromWP
                track[steps-1] = toWP
                latDelta = (toWP[0]-fromWP[0])/(steps-1)
                lngDelta = (toWP[1]-fromWP[1])/(steps-1)
                for i in range(1, steps-1):
                    prvs = track[i-1]
                    lat = prvs[0]+latDelta
                    lng = prvs[1]+lngDelta
                    track[i] = (lat, lng)
                return track
            else:
                logging.critical('Waypoint is out of scope: '+str(toWP))
                return []
        else:
            logging.critical('Waypoint is out of scope: '+str(fromWP))
            return []


    def build_route(self, route_name: str, waypoints: list):
        """
        build the tracks for the route defined in 'waypoints',
        which is a list of waypoint tuples (lat, lon)
        """
        route = {
            "name": route_name,
            "waypoints": waypoints,
            "tracks": []
        }
        prvsWP = None
        for waypoint in waypoints:
            if prvsWP: # not empty
                # append tracks
                tracks = self.build_tracks(prvsWP, waypoint)
                if route["tracks"]: # not empty
                    # last item is same as first item in next tracks list 
                    del route["tracks"][-1]    # delete redundant item                     
                route["tracks"].extend(tracks) # append next tracks list
            prvsWP = waypoint
        #
        return route


# main ========

if __name__ == '__main__':
    print("This Routes class module shall not be invoked on it's own.")
        