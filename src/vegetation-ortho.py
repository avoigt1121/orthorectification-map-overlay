import rasterio
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import os
#Loads the Bands in Python
from pathlib import Path

# repo root = current file's parent, climbing up if needed
ROOT = Path(__file__).resolve().parent.parent
data_filepath = ROOT / "src" / "usgs_data"
aligned_filepath = ROOT / "data" / "aligned_bands"

# Check if aligned bands are available
use_aligned = aligned_filepath.exists() and any(aligned_filepath.glob("*_aligned.TIF"))

if use_aligned:
    print("✅ Using aligned bands from:", aligned_filepath)
    data_source = aligned_filepath
    b4_pattern = "*_B4_aligned.TIF"
    b5_pattern = "*_B5_aligned.TIF"
else:
    print("Using original bands from:", data_filepath)
    data_source = data_filepath
    b4_pattern = "*B4.TIF"
    b5_pattern = "*B5.TIF"

b4_files = [os.path.join(data_source, f) 
            for f in os.listdir(data_source) 
            if f.endswith(".TIF") and ("B4" in f)]

# Filter for the correct pattern
if use_aligned:
    b4_files = [f for f in b4_files if "_aligned.TIF" in f]
else:
    b4_files = [f for f in b4_files if "_aligned.TIF" not in f]

print(f"Found {len(b4_files)} Landsat scenes to process")

j=1
for i in b4_files:
    print(f"Processing scene {j}/{len(b4_files)}: {os.path.basename(i)}")
    red_path = i
    
    if use_aligned:
        nir_path = red_path.replace('_B4_aligned.TIF','_B5_aligned.TIF')
    else:
        nir_path = red_path.replace('B4.TIF','B5.TIF')

    print(f"  Loading Red band: {os.path.basename(red_path)}")
    with rasterio.open(red_path) as red_src:
        red = red_src.read(1).astype(float)
        profile = red_src.profile  # keep georeference info

    print(f"  Loading NIR band: {os.path.basename(nir_path)}")
    with rasterio.open(nir_path) as nir_src:
        nir = nir_src.read(1).astype(float)

    print(f"  Calculating NDVI...")
    #Compute NDVI - or Normalized Difference Vegetation Index, is a remote sensing indicator that measures vegetation health, density, and greenness

    np.seterr(divide='ignore', invalid='ignore')  # suppress warnings

    ndvi = (nir - red) / (nir + red)

# Optional: mask pixels where NIR + Red == 0
    ndvi[(nir + red) == 0] = np.nan 
        # Add to your existing script
    assert -1 <= np.nanmin(ndvi) <= 1, "NDVI values out of range"
    assert -1 <= np.nanmax(ndvi) <= 1, "NDVI values out of range"
    print(f"NDVI values in valid range: {np.nanmin(ndvi):.3f} to {np.nanmax(ndvi):.3f}")

    profile.update(dtype=rasterio.float32, count=1)

    print(f"  Saving NDVI raster: data/ndvi_{j}.tif")
    #save NDVI as geotiff
    os.makedirs('data', exist_ok=True)  # Ensure data directory exists
    with rasterio.open(f"data/ndvi_{j}.tif", 'w', **profile) as dst:
        dst.write(ndvi.astype(rasterio.float32), 1)
    j=j+1
    #visualize and save plot
    plt.figure(figsize=(10, 8))
    plt.imshow(ndvi, cmap="RdYlGn")
    plt.colorbar(label="NDVI")
    plt.title("NDVI")
    plt.savefig(f"data/ndvi_plot_{j-1}.png", dpi=300, bbox_inches='tight')
    plt.close()  # Close the figure to free memory
    print(f"NDVI plot saved as data/ndvi_plot_{j-1}.png")
