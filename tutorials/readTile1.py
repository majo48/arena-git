#!/usr/bin/env python3

"""
    Read Copernicus tile data
"""

import os
import sys

tile_path = "/mnt/d/myprojects/vps-git/cmd/getCOGdata/"
tiles = ["tile1/", "tile2/"]

def main():

    print('Read Copernicus Tile data.')
    for tile in tiles:
        print(os.listdir(tile_path+tile)) # print contents of tile folder


if __name__ == '__main__':
    sys.exit(main())
