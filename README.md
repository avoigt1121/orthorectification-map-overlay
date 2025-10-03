# Vegetation Monitoring with Landsat

Simple Python scripts for downloading and processing Landsat satellite data to calculate vegetation indices.

## Files

- `api.py` - Search for Landsat scenes using USGS API
- `vegetation-ortho.py` - Calculate NDVI from Landsat bands
- `src/georeference_analysis.py` - Analyze band alignment and georeference info
- `src/band_aligner.py` - Align misaligned Landsat bands
- `tests/alignment_testing.py` - Test suite for checking band alignment
- `requirements.txt` - Python dependencies

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get Landsat data:**
   - Download from [USGS EarthExplorer](https://earthexplorer.usgs.gov/)
   - Extract `.tar` files to `data/`
   - Look for files ending in `B4.TIF` (red) and `B5.TIF` (near-infrared)

3. **Check band alignment:**
   ```bash
   python tests/alignment_testing.py
   ```

4. **Run vegetation analysis:**
   ```bash
   python vegetation-ortho.py
   ```

## What It Does

- **Finds and analyzes** Landsat bands for alignment issues
- **Aligns misaligned bands** using reprojection if needed
- **Calculates NDVI** using red and near-infrared bands
- **Saves results** as GeoTIFF files and visualizations

## Output

- `data/ndvi_*.tif` - NDVI raster files (can open in QGIS)
- `data/ndvi_plot_*.png` - NDVI visualizations
- `data/aligned_bands/` - Aligned band files (if alignment was needed)
- `data/alignment_report.txt` - Band alignment test results

## Coordinates

All data uses **WGS84** coordinate system (standard GPS coordinates).
