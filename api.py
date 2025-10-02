#!/usr/bin/env python3
"""
Simple USGS API for Vegetation Data

Get your M2M token at: https://m2m.cr.usgs.gov/
Navigate to: Machine to Machine > Access Token > Generate Token
"""

import requests
from datetime import datetime, timedelta

class VegetationAPI:
    def __init__(self, token: str):
        self.base_url = "https://m2m.cr.usgs.gov/api/api/json/stable/"
        self.token = token
        
    def search_scenes(self, bbox, start_date: str, end_date: str, max_cloud: int = 20):
        """
        Search for Landsat vegetation scenes
        
        Args:
            bbox: (min_lon, min_lat, max_lon, max_lat) in WGS84
            start_date: "YYYY-MM-DD" 
            end_date: "YYYY-MM-DD"
            max_cloud: Maximum cloud cover %
        
        Returns:
            List of scenes
        """
        url = f"{self.base_url}scene-search"
        
        payload = {
            "apiKey": self.token,
            "datasetName": "landsat_ot_c2_l2",
            "spatialFilter": {
                "filterType": "mbr",
                "lowerLeft": {"latitude": bbox[1], "longitude": bbox[0]},
                "upperRight": {"latitude": bbox[3], "longitude": bbox[2]}
            },
            "temporalFilter": {"startDate": start_date, "endDate": end_date},
            "sceneFilter": {"cloudCover": {"min": 0, "max": max_cloud}},
            "maxResults": 25
        }
        
        response = requests.post(url, json=payload)
        result = response.json()
        
        if result.get('errorCode'):
            print(f"Search failed: {result.get('errorMessage')}")
            return []
            
        return result.get('data', {}).get('results', [])
    
    def get_scene_info(self, scene):
        """Extract key info from scene metadata"""
        return {
            'scene_id': scene.get('displayId', 'N/A'),
            'date': scene.get('temporalCoverage', {}).get('startDate', 'N/A'),
            'cloud_cover': scene.get('cloudCover', 'N/A'),
            'path': scene.get('spatialCoverage', {}).get('path', 'N/A'),
            'row': scene.get('spatialCoverage', {}).get('row', 'N/A')
        }


def main():
    """Simple example usage"""
    # Get your token from: https://m2m.cr.usgs.gov/
    token = input("Enter your M2M token: ").strip()
    
    if not token:
        print("No token provided.")
        return
    
    # Initialize API
    api = VegetationAPI(token)
    
    # San Francisco Bay Area
    bbox = (-122.6, 37.6, -122.2, 37.9)
    
    # Last 60 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    
    print(f"\nSearching for Landsat scenes...")
    print(f"Area: {bbox}")
    print(f"Dates: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    scenes = api.search_scenes(
        bbox, 
        start_date.strftime('%Y-%m-%d'), 
        end_date.strftime('%Y-%m-%d'),
        max_cloud=15
    )
    
    if scenes:
        print(f"\nFound {len(scenes)} scenes:")
        for i, scene in enumerate(scenes[:5], 1):
            info = api.get_scene_info(scene)
            print(f"{i}. {info['scene_id']} - {info['date']} - {info['cloud_cover']}% clouds")
    else:
        print("No scenes found.")


if __name__ == "__main__":
    main()
