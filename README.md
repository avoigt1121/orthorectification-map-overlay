# Vegetation Monitoring with Landsat

Simple Python scripts for downloading and processing Landsat satellite data to calculate vegetation indices.

## Files

- `api.py` - Search for Landsat scenes using USGS API
- `vegetation-ortho.py` - Calculate NDVI from Landsat bands
- `requirements.txt` - Python dependencies

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get Landsat data:**
   - Download from [USGS EarthExplorer](https://earthexplorer.usgs.gov/)
   - Extract `.tar` files to `/Users/annivoigt/Documents/data/`
   - Look for files ending in `B4.TIF` (red) and `B5.TIF` (near-infrared)

3. **Run vegetation analysis:**
   ```bash
   python vegetation-ortho.py
   ```

## What It Does

- Finds all Landsat Band 4 (red) files in your data folder
- Calculates NDVI using red and near-infrared bands
- Saves NDVI as GeoTIFF files in `data/` folder
- Creates visualization plots as PNG files

## Output

- `data/ndvi_0.tif` - NDVI raster (can open in QGIS)
- `data/ndvi_plot_0.png` - NDVI visualization

## Coordinates

All data uses **WGS84** coordinate system (standard GPS coordinates).
