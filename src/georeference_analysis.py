#!/usr/bin/env python3
"""
Simple Georeference Analysis for Landsat TIF Files
"""

import rasterio
from rasterio.crs import CRS
from rasterio.warp import transform_bounds
from pathlib import Path
from typing import Tuple, Dict, Union, Optional
import itertools
import os

class GeoInfo:
    """Simple georeference information extractor"""
    
    def __init__(self, filepath: Union[str, Path]):
        self.filepath = str(filepath)
        
    def get_info(self) -> Dict:
        """Get all georeference info in one call"""
        with rasterio.open(self.filepath) as src:
            # Get bounds in WGS84
            if src.crs != CRS.from_epsg(4326):
                west, south, east, north = transform_bounds(
                    src.crs, CRS.from_epsg(4326), *src.bounds
                )
            else:
                west, south, east, north = src.bounds
            
            return {
                'file': Path(self.filepath).name,
                'crs': str(src.crs),
                'bounds_wgs84': (west, south, east, north),
                'center_wgs84': ((west + east) / 2, (south + north) / 2),
                'shape': (src.height, src.width),
                'pixel_size': (abs(src.transform[0]), abs(src.transform[4]))
            }


class SceneAnalyzer:
    """Analyze multiple Landsat bands together"""
    
    def __init__(self, bands: Dict[str, Path]):
        self.bands = bands
    
    def find_bands(self) -> Dict[str, Path]:
        """Return the bands"""
        return self.bands
    
    def check_alignment(self) -> bool:
        """Check if bands are aligned (same bounds and shape)"""
        bands = self.find_bands()
        if len(bands) < 2:
            return True
            
        # Get info for first band as reference
        first_band = list(bands.values())[0]
        ref_info = GeoInfo(first_band).get_info()
        
        # Check all other bands match
        for band_file in list(bands.values())[1:]:
            band_info = GeoInfo(band_file).get_info()
            if (band_info['bounds_wgs84'] != ref_info['bounds_wgs84'] or 
                band_info['shape'] != ref_info['shape']):
                return False
        
        return True
    
    def get_summary(self) -> Dict:
        """Get scene summary"""
        bands = self.find_bands()
        if not bands:
            return {'error': 'No bands found'}
        
        # Use first band for georeference info
        first_band = list(bands.values())[0]
        geo_info = GeoInfo(first_band).get_info()
        
        return {
            'bands_found': list(bands.keys()),
            'bands_aligned': self.check_alignment(),
            'georeference': geo_info
        }


class AlignmentChecker:
    """Simple checker to see which bands are misaligned"""
    
    def __init__(self, bands: Dict[str, Path]):
        self.bands = bands
    
    def check_crs(self):
        """Check if all bands have consistent CRS"""
        if len(self.bands) < 2:
            print("Only one band found")
            return
        
        # Get CRS for each band
        ref_band = list(self.bands.keys())[0]
        ref_info = GeoInfo(self.bands[ref_band]).get_info()
        ref_crs = ref_info['crs']
        
        print(f"CRS Consistency Check (reference: {ref_band})")
        print(f"Reference CRS: {ref_crs}")
        
        crs_consistent = True
        for band_name, band_file in self.bands.items():
            if band_name == ref_band:
                continue
            
            band_info = GeoInfo(band_file).get_info()
            
            if band_info['crs'] != ref_crs:
                print(f"  ❌ {band_name}: Different CRS ({band_info['crs']})")
                crs_consistent = False
            else:
                print(f"  ✅ {band_name}: Same CRS")
        
        if crs_consistent:
            print("✅ All bands have consistent CRS")
        else:
            print("❌ CRS mismatches detected")
    
    def check_raw_bounds(self):
        """Check raw coordinate bounds in native CRS (before WGS84 transformation)"""
        if len(self.bands) < 2:
            print("Only one band found")
            return
        
        print("Raw Coordinate Bounds (Native CRS):")
        print("-" * 40)
        
        # Get raw bounds for each band
        ref_band = list(self.bands.keys())[0]
        ref_bounds = None
        
        for band_name, band_file in self.bands.items():
            with rasterio.open(band_file) as src:
                # Get raw bounds (no transformation)
                bounds = src.bounds
                crs = str(src.crs)
                
                print(f"{band_name}:")
                print(f"  CRS: {crs}")
                print(f"  Raw bounds: ({bounds.left:.6f}, {bounds.bottom:.6f}, {bounds.right:.6f}, {bounds.top:.6f})")
                
                # Store reference for comparison
                if band_name == ref_band:
                    ref_bounds = bounds
                    ref_crs = crs
                else:
                    # Compare to reference
                    if ref_bounds:
                        max_diff = max(
                            abs(bounds.left - ref_bounds.left),
                            abs(bounds.bottom - ref_bounds.bottom),
                            abs(bounds.right - ref_bounds.right),
                            abs(bounds.top - ref_bounds.top)
                        )
                        print(f"  Difference from {ref_band}: {max_diff:.6f} units")
                print()
        
        print("Note: These are raw bounds in the native CRS before any coordinate transformation.")
    
    def check(self):
        """Check spatial alignment and print results"""
        if len(self.bands) < 2:
            print("Only one band found")
            return
        
        # Compare all bands to first one
        ref_band = list(self.bands.keys())[0]
        ref_info = GeoInfo(self.bands[ref_band]).get_info()
        
        print(f"Spatial Alignment Check (reference: {ref_band})")
        
        all_aligned = True
        for band_name, band_file in self.bands.items():
            if band_name == ref_band:
                continue
            
            band_info = GeoInfo(band_file).get_info()
            
            # Check spatial alignment
            bounds_match = ref_info['bounds_wgs84'] == band_info['bounds_wgs84']
            shape_match = ref_info['shape'] == band_info['shape']
            
            if not (bounds_match and shape_match):
                print(f"  ❌ {band_name}: Spatially misaligned")
                all_aligned = False
                
                # Show how much they differ
                ref_bounds = ref_info['bounds_wgs84']
                band_bounds = band_info['bounds_wgs84']
                max_diff = max(
                    abs(ref_bounds[0] - band_bounds[0]),  # west
                    abs(ref_bounds[1] - band_bounds[1]),  # south
                    abs(ref_bounds[2] - band_bounds[2]),  # east
                    abs(ref_bounds[3] - band_bounds[3])   # north
                )
                print(f"    Bounds differ by: {max_diff:.2e} degrees")
                
                if ref_info['shape'] != band_info['shape']:
                    print(f"    Shape: {ref_info['shape']} vs {band_info['shape']}")
        
        if all_aligned:
            print("  ✅ All bands are spatially aligned")
        


def demo():
    """Simple demo"""
    mypath = str(os.getcwd())
    data_dir = Path(mypath + "/data/aligned_bands")
    # Find aligned bands with same filename prefix
    bands = {}
    import re
    # Group files by their prefix (everything before _B)
    file_groups = {}
    patterns = ["*_B*_aligned.TIF", "*_B*.TIF"]
    combined_files = itertools.chain.from_iterable(data_dir.glob(p) for p in patterns)
    for file in combined_files:
        match = re.search(r'(.+)_B(\d+)(_aligned)?\.TIF$', file.name)
        if match:
            prefix = match.group(1)  # Everything before _B
            band_num = match.group(2)  # The number after B
            
            if prefix not in file_groups:
                file_groups[prefix] = {}
            file_groups[prefix][f'B{band_num}'] = file
    
    # Use the group with the most bands
    for i in file_groups:
        print(i)
        bands = file_groups[i]
        print("Files being compared:")
        for band, file in bands.items():
            print(f"  {band}: {file.name}")
        print(f"Found bands: {list(bands.keys())}")

        # Analyze first file
        first_band = list(bands.values())[0]
        geo = GeoInfo(first_band)
        info = geo.get_info()

        # Check alignment
        scene = SceneAnalyzer(bands)
        aligned = scene.check_alignment()
        print(f"Aligned: {aligned}")

        # Now use the same bands dictionary for AlignmentChecker
        checker = AlignmentChecker(bands)
        checker.check()    

if __name__ == "__main__":
    demo()
