#!/usr/bin/env python3
"""
Simple script to show TIF file coordinates
"""

import rasterio
from pathlib import Path
import math

def show_coordinates(tif_file):
    """Show coordinates for one TIF file"""
    with rasterio.open(tif_file) as src:
        # Get bounds in WGS84
        if src.crs.to_epsg() != 4326:
            from rasterio.warp import transform_bounds
            west, south, east, north = transform_bounds(src.crs, 'EPSG:4326', *src.bounds)
        else:
            west, south, east, north = src.bounds
        
        # Center point
        center_lat = (south + north) / 2
        center_lon = (west + east) / 2
        
        # Which elevation tile you need (format like 33, -117)
        tile_lat = math.floor(center_lat)
        tile_lon = math.floor(center_lon)
        
        print(f"Elevation tile needed: {tile_lat}, {tile_lon}")

def main():
    """Find and show coordinates for all TIF files"""
    data_dir = Path("/Users/annivoigt/Documents/GitHub/mini-orthorectifaction-map-overlay/src/usgs_data/n40_w125_1arc_v3.dt2")

    # Find TIF files
    tif_files = list(data_dir.glob("**/*.TIF")) + list(data_dir.glob("**/*.tif"))
    
    print(f"Found {len(tif_files)} TIF files:")
    print()
    
    for tif_file in tif_files:
        show_coordinates(tif_file)

if __name__ == "__main__":
    main()
