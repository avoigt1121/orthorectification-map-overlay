import rasterio
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import os
#Loads the Bands in Python
data_filepath = '/tree/data/'


b4_files = [os.path.join(data_filepath, f) 
            for f in os.listdir(data_filepath) 
            if "B4" in f and f.endswith(".TIF")]

print(f"Found {len(b4_files)} Landsat scenes to process")

j=1
for i in b4_files:
    print(f"Processing scene {j+1}/{len(b4_files)}: {os.path.basename(i)}")
    red_path = i
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
    ndvi = np.clip(ndvi, -1, 1)  # optional, just to limit values

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
