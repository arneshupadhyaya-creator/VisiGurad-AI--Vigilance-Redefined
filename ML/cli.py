import sys
import os
import json
from PIL import Image

# Ensure the ML directory is in the import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ELA import generate_ela
except ImportError as e:
    print(json.dumps({"success": False, "error": f"Failed to import generate_ela: {str(e)}"}))
    sys.exit(1)

def calculate_threat_score(ela_image):
    """
    Analyzes the ELA image to calculate a threat score between 0 and 100.
    Looks at the density of bright/high-contrast pixels in the error map.
    """
    try:
        # Convert to grayscale to evaluate pixel intensities
        gray_image = ela_image.convert('L')
        pixels = list(gray_image.getdata())
        
        # Count pixels that have substantial difference (intensity > 30 out of 255)
        total_pixels = len(pixels)
        if total_pixels == 0:
            return 0
            
        anomalous_pixels = sum(1 for p in pixels if p > 30)
        percentage = (anomalous_pixels / total_pixels) * 100
        
        # Map percentage to threat score:
        # Standard JPEG compression has minor ELA difference throughout.
        # High concentrations (hotspots) will drive the score up.
        threat_score = min(100, percentage * 5.0) # scaling factor
        return round(threat_score, 2)
    except Exception:
        return 0.0

def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "success": False,
            "error": "Usage: python cli.py <input_path> <output_path> [quality]"
        }))
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    quality = int(sys.argv[3]) if len(sys.argv) > 3 else 90
    
    if not os.path.exists(input_path):
        print(json.dumps({
            "success": False,
            "error": f"Input file not found: {input_path}"
        }))
        sys.exit(1)
        
    try:
        # Generate the ELA map
        ela_img = generate_ela(input_path, quality=quality)
        
        # Save ELA map to the designated output path
        ela_img.save(output_path)
        
        # Calculate threat score
        threat_score = calculate_threat_score(ela_img)
        
        # Determine threat status
        if threat_score < 15:
            status = "Clean"
        elif threat_score < 45:
            status = "Suspicious"
        else:
            status = "Tampered"
            
        print(json.dumps({
            "success": True,
            "threatScore": threat_score,
            "status": status,
            "message": "Error Level Analysis generated successfully."
        }))
        
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": f"Error running ELA analysis: {str(e)}"
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
