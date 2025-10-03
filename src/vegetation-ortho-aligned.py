#!/usr/bin/env python3
"""
Process Landsat bands to calculate NDVI with alignment correction
"""

import rasterio
from rasterio.warp import reproject, Resampling
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path
import os


def align_band_to_reference(band_file, reference_file, output_file):
    """Align a band to match the georeference of a reference band"""
    print(f"Aligning {band_file.name} to match {reference_file.name}...")
    
    with rasterio.open(reference_file) as ref:
        ref_transform = ref.transform
        ref_crs = ref.crs
        ref_width = ref.width
        ref_height = ref.height
        
        with rasterio.open(band_file) as src:
            # Create aligned array
            aligned_data = np.zeros((ref_height, ref_width), dtype=src.dtypes[0])
            
            # Reproject to match reference
            reproject(
                source=rasterio.band(src, 1),
                destination=aligned_data,
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=ref_transform,
                dst_crs=ref_crs,
                resampling=Resampling.bilinear
            )
            
            # Save aligned band
            with rasterio.open(
                output_file,
                'w',
                driver='GTiff',
                height=ref_height,
                width=ref_width,
                count=1,
                dtype=aligned_data.dtype,
                crs=ref_crs,
                transform=ref_transform,
            ) as dst:
                dst.write(aligned_data, 1)
    
    print(f"  ✅ Saved aligned band: {output_file}")


def process_aligned_ndvi():
    """Process NDVI with band alignment"""
    # Setup paths
    ROOT = Path(__file__).resolve().parent.parent
    data_filepath = ROOT / "src" / "usgs_data"
    output_dir = ROOT / "data"
    aligned_dir = output_dir / "aligned_bands"
    
    # Create directories
    output_dir.mkdir(exist_ok=True)
    aligned_dir.mkdir(exist_ok=True)
    
    # Find B4 files
    b4_files = [data_filepath / f 
                for f in os.listdir(data_filepath) 
                if "B4" in f and f.endswith(".TIF")]
    
    print(f"Found {len(b4_files)} Landsat scenes to process with alignment")
    
    for i, red_path in enumerate(b4_files):
        scene_name = red_path.name.replace('_SR_B4.TIF', '')
        print(f"\nProcessing scene {i+1}/{len(b4_files)}: {scene_name}")
        
        # Find corresponding B5 file
        nir_path = Path(str(red_path).replace('B4.TIF', 'B5.TIF'))
        
        if not nir_path.exists():
            print(f"  ❌ No matching B5 file found for {red_path.name}")
            continue
        
        # Aligned file paths
        aligned_red = aligned_dir / f"{scene_name}_B4_aligned.TIF"
        aligned_nir = aligned_dir / f"{scene_name}_B5_aligned.TIF"
        
        # Use B4 as reference, align B5 to match
        print(f"  Using B4 as reference, aligning B5...")
        align_band_to_reference(nir_path, red_path, aligned_nir)
        
        # Copy B4 as reference (or you could align both to a common grid)
        print(f"  Copying reference B4...")
        with rasterio.open(red_path) as src:
            with rasterio.open(aligned_red, 'w', **src.profile) as dst:
                dst.write(src.read())
        
        # Calculate NDVI from aligned bands
        print(f"  Calculating NDVI from aligned bands...")
        with rasterio.open(aligned_red) as red_src:
            red = red_src.read(1).astype(float)
            profile = red_src.profile
            
        with rasterio.open(aligned_nir) as nir_src:
            nir = nir_src.read(1).astype(float)
        
        # Calculate NDVI
        ndvi = (nir - red) / (nir + red)
        
        # Handle division by zero
        ndvi = np.where((nir + red) == 0, 0, ndvi)
        
        # Save NDVI
        ndvi_output = output_dir / f"ndvi_aligned_{scene_name}.tif"
        profile.update(dtype=rasterio.float32, count=1)
        
        with rasterio.open(ndvi_output, 'w', **profile) as ndvi_dst:
            ndvi_dst.write(ndvi.astype(rasterio.float32), 1)
        
        print(f"  ✅ NDVI saved: {ndvi_output}")


if __name__ == "__main__":
    process_aligned_ndvi()
    print("\nDone! Check the 'data/aligned_bands/' directory for aligned bands.")
    print("NDVI files with 'aligned' prefix use properly aligned bands.")
