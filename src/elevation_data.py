from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt

# Open your DEM GeoTIFF
dataset = gdal.Open("/Users/annivoigt/Documents/GitHub/mini-orthorectifaction-map-overlay/src/usgs_data/n36_w117_1arc_v3.tif")

# Read the first (and usually only) band
band = dataset.GetRasterBand(1)
elevation = band.ReadAsArray()

# Basic info
print("Shape:", elevation.shape)
print("Elevation range:", np.nanmin(elevation), "to", np.nanmax(elevation))

# Plot grayscale elevation
plt.imshow(elevation, cmap='gray')
plt.title("Elevation (m)")
plt.colorbar(label='Meters')
plt.show()


from osgeo import gdal
gdal.DEMProcessing(
    "data/hillshade.tif",        # output file
    "usgs_data/your_dem.tif",         # input DEM
    "data/hillshade",            # processing mode
    azimuth=315,            # direction of sunlight (degrees)
    altitude=45             # height of the sun above horizon
)

# Display hillshade
hillshade = gdal.Open("data/hillshade.tif").ReadAsArray()
plt.imshow(hillshade, cmap='gray')
plt.title("Hillshade")
plt.show()

gdal.DEMProcessing(
    "color_relief.tif",
    "your_dem.tif",
    "color-relief",
    colorFilename="color_relief.txt"
)

# Display
color_relief = gdal.Open("color_relief.tif").ReadAsArray()
plt.imshow(np.transpose(color_relief, (1, 2, 0)))  # reorder RGB
plt.title("Color Relief")
plt.show()
