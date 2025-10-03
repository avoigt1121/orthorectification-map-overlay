#!/usr/bin/env python3
"""
Band Alignment Class for Landsat Data
"""

import rasterio
from rasterio.warp import reproject, Resampling
import numpy as np
from pathlib import Path
import os
from typing import Union, List, Dict, Optional


class BandAligner:
    """Align Landsat bands to ensure perfect spatial registration"""
    
    def __init__(self, data_dir: Union[str, Path], output_dir: Optional[Union[str, Path]] = None):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir) if output_dir else self.data_dir.parent / "data" / "aligned_bands"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all band files
        self.scenes = self._find_scenes()
    
    def _find_scenes(self) -> Dict[str, Dict[str, Path]]:
        """Find all scenes and their band files"""
        scenes = {}
        
        # Find all B4 files as scene identifiers
        for file in self.data_dir.glob("*_SR_B4.TIF"):
            scene_name = file.name.replace('_SR_B4.TIF', '')
            scenes[scene_name] = {'B4': file}
            
            # Find corresponding B5 file
            b5_file = self.data_dir / file.name.replace('B4.TIF', 'B5.TIF')
            if b5_file.exists():
                scenes[scene_name]['B5'] = b5_file
        
        return scenes
    
    def align_band_to_reference(self, band_file: Path, reference_file: Path, output_file: Path):
        """Align a single band to match reference geometry"""
        print(f"  Aligning {band_file.name} to match {reference_file.name}...")
        
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
                
                # Save aligned band with reference profile
                profile = ref.profile.copy()
                profile.update(dtype=aligned_data.dtype)
                
                with rasterio.open(output_file, 'w', **profile) as dst:
                    dst.write(aligned_data, 1)
        
        print(f"    ✅ Saved: {output_file.name}")
    
    def align_scene(self, scene_name: str, reference_band: str = 'B4'):
        """Align all bands in a scene to the reference band"""
        if scene_name not in self.scenes:
            print(f"Scene {scene_name} not found")
            return
        
        scene_bands = self.scenes[scene_name]
        if reference_band not in scene_bands:
            print(f"Reference band {reference_band} not found in scene {scene_name}")
            return
        
        print(f"Aligning scene: {scene_name} (reference: {reference_band})")
        
        reference_file = scene_bands[reference_band]
        aligned_files = {}
        
        for band_name, band_file in scene_bands.items():
            aligned_file = self.output_dir / f"{scene_name}_{band_name}_aligned.TIF"
            
            if band_name == reference_band:
                # Copy reference band as-is
                print(f"  Copying reference {band_name}...")
                with rasterio.open(band_file) as src:
                    with rasterio.open(aligned_file, 'w', **src.profile) as dst:
                        dst.write(src.read())
                print(f"    ✅ Saved: {aligned_file.name}")
            else:
                # Align to reference
                self.align_band_to_reference(band_file, reference_file, aligned_file)
            
            aligned_files[band_name] = aligned_file
        
        return aligned_files
    
    def align_all_scenes(self, reference_band: str = 'B4'):
        """Align all scenes found in the data directory"""
        print(f"Found {len(self.scenes)} scenes to align")
        print(f"Output directory: {self.output_dir}")
        print("-" * 50)
        
        aligned_scenes = {}
        
        for scene_name in self.scenes.keys():
            try:
                aligned_files = self.align_scene(scene_name, reference_band)
                aligned_scenes[scene_name] = aligned_files
                print(f"✅ Scene {scene_name} aligned successfully\n")
            except Exception as e:
                print(f"❌ Error aligning scene {scene_name}: {e}\n")
        
        return aligned_scenes
    
    def get_aligned_scene_paths(self, scene_name: str) -> Dict[str, Path]:
        """Get paths to aligned band files for a scene"""
        aligned_paths = {}
        for band in ['B4', 'B5']:
            aligned_file = self.output_dir / f"{scene_name}_{band}_aligned.TIF"
            if aligned_file.exists():
                aligned_paths[band] = aligned_file
        return aligned_paths
    
    def list_scenes(self):
        """List all available scenes"""
        print("Available scenes:")
        for scene_name, bands in self.scenes.items():
            band_list = list(bands.keys())
            print(f"  {scene_name}: {band_list}")


def demo():
    """Demo the BandAligner class"""
    # Setup paths
    data_dir = Path("usgs_data")
    
    if not data_dir.exists():
        print(f"Data directory {data_dir} not found")
        return
    
    # Create aligner
    aligner = BandAligner(data_dir)
    
    # List available scenes
    aligner.list_scenes()
    print()
    
    # Align all scenes
    aligned_scenes = aligner.align_all_scenes()
    
    print(f"Alignment complete! {len(aligned_scenes)} scenes processed.")
    print(f"Aligned bands saved to: {aligner.output_dir}")


if __name__ == "__main__":
    demo()
