#!/usr/bin/env python3
"""
Simple elevation file stitcher using GDAL
"""

from osgeo import gdal
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def stitch_elevation_files():
    """Stitch all elevation files in data/elevation directory"""
    # Find elevation files
    elevation_dir = Path("/Users/annivoigt/Documents/GitHub/mini-orthorectifaction-map-overlay/src/elevation_data")
    if not elevation_dir.exists():
        elevation_dir = Path("../data")
    
    files = list(elevation_dir.glob("*.tif")) + list(elevation_dir.glob("*.hgt"))
    
    if not files:
        print("No elevation files found")
        return
    
    print(f"Found {len(files)} files:")
    
    # Check file sizes first
    total_size = 0
    for f in files:
        size_mb = f.stat().st_size / (1024 * 1024)
        total_size += size_mb
        print(f"  {f.name} ({size_mb:.1f} MB)")
    
    print(f"\nTotal input size: {total_size:.1f} MB")
    
    if total_size > 5000:  # More than 5GB
        print("⚠️  WARNING: Input files are very large!")
        print("This will create a huge mosaic. Consider:")
        print("1. Using fewer files")
        print("2. Downsampling (reduce resolution)")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Create VRT and stitch with compression + downsampling
    output_path = elevation_dir / "elevation_mosaic.tif"
    file_paths = [str(f) for f in files]
    
    gdal.UseExceptions()
    vrt_ds = gdal.BuildVRT("temp.vrt", file_paths)
    
    # Add compression options to make file much smaller
    translate_options = gdal.TranslateOptions(
        format='GTiff',
        creationOptions=[
            'COMPRESS=LZW',      # Lossless compression
            'TILED=YES',         # Better performance
            'PREDICTOR=2'        # Better compression for elevation data
        ],
        xRes=0.001,              # Downsample to ~100m resolution (0.001 degrees)
        yRes=0.001               # This reduces file size dramatically
    )
    
    gdal.Translate(str(output_path), vrt_ds, options=translate_options)
    
    print(f"✅ Mosaic saved: {output_path}")
    
    # Simple visualization
    ds = gdal.Open(str(output_path))
    elevation = ds.GetRasterBand(1).ReadAsArray()
    
    plt.figure(figsize=(10, 6))
    plt.imshow(elevation, cmap='terrain')
    plt.colorbar(label='Elevation (m)')
    plt.title('Elevation Mosaic')
    plt.savefig(elevation_dir / "elevation_mosaic.png")
    plt.show()
    
    print("✅ Visualization saved")

if __name__ == "__main__":
    stitch_elevation_files()
