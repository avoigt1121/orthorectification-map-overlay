import os
import sys
import re
import itertools
from typing import Dict
from pathlib import Path

# Add project root to Python path so we can import from src
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from src.georeference_analysis import GeoInfo, SceneAnalyzer, AlignmentChecker


class TestSuite:
    """Comprehensive alignment testing framework"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.results = []
    
    def run_all_tests(self):
        """Run all alignment tests on all discovered scenes"""
        data_dir = Path(str(project_root) + "/src/data/aligned_bands")
        print(data_dir)
        # Find aligned bands with same filename prefix
        bands = {}
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
        
    def test_scene_alignment(self, scene_bands: dict):
        """Test alignment for a single scene"""
        print(f"\n=== Testing Scene Alignment ===")
        print(f"Bands: {list(scene_bands.keys())}")
        
        # Test 1: Basic alignment check using SceneAnalyzer
        scene_analyzer = SceneAnalyzer(scene_bands)
        is_aligned = scene_analyzer.check_alignment()
        print(f"✅ Basic alignment: {is_aligned}")
        
        # Test 2: Detailed alignment check using AlignmentChecker
        checker = AlignmentChecker(scene_bands)
        print(f"\n--- CRS Consistency ---")
        checker.check_crs()
        
        print(f"\n--- Spatial Alignment ---")
        checker.check()
        
        print(f"\n--- Raw Bounds Check ---")
        checker.check_raw_bounds()
        
        # Store result
        result = {
            'scene': list(scene_bands.keys()),
            'aligned': is_aligned,
            'bands_count': len(scene_bands)
        }
        self.results.append(result)
        
        return is_aligned
        
    def generate_report(self):
        """Generate comprehensive test report"""
        print(f"\n{'='*50}")
        print(f"ALIGNMENT TEST REPORT")
        print(f"{'='*50}")
        
        if not self.results:
            print("No test results found. Run tests first.")
            return
        
        total_scenes = len(self.results)
        aligned_scenes = sum(1 for r in self.results if r['aligned'])
        misaligned_scenes = total_scenes - aligned_scenes
        
        print(f"\nSUMMARY:")
        print(f"  Total scenes tested: {total_scenes}")
        print(f"  ✅ Aligned scenes: {aligned_scenes}")
        print(f"  ❌ Misaligned scenes: {misaligned_scenes}")
        print(f"  Success rate: {(aligned_scenes/total_scenes)*100:.1f}%")
        
        print(f"\nDETAILS:")
        for i, result in enumerate(self.results, 1):
            status = "✅ ALIGNED" if result['aligned'] else "❌ MISALIGNED"
            bands_str = ", ".join(result['scene'])
            print(f"  Scene {i}: {status}")
            print(f"    Bands: {bands_str} ({result['bands_count']} bands)")
        
        # Save to file
        report_file = self.data_dir / "alignment_report.txt"
        with open(report_file, 'w') as f:
            f.write(f"Alignment Test Report\n")
            f.write(f"Generated: {os.getcwd()}\n")
            f.write(f"Total scenes: {total_scenes}\n")
            f.write(f"Aligned: {aligned_scenes}\n")
            f.write(f"Misaligned: {misaligned_scenes}\n")
            f.write(f"Success rate: {(aligned_scenes/total_scenes)*100:.1f}%\n")
        
        print(f"\n📄 Report saved to: {report_file}")
        return self.results


def main():
    """Run alignment tests from command line"""
    # Set up data directory
    data_dir = Path(str(project_root) + "/src/data/aligned_bands")
    
    print(f"🔍 Looking for test files in: {data_dir}")
    
    # Create test suite
    test_suite = TestSuite(data_dir)
    
    # Run all tests
    test_suite.run_all_tests()
    
    # Generate report
    test_suite.generate_report()


if __name__ == "__main__":
    main()