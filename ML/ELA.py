import os
from PIL import Image, ImageChops

def generate_ela(image_path, quality=90):
    """
    Performs Error Level Analysis (ELA) to expose digital modifications.
    
    :param image_path: Path to the input image file
    :param quality: Resave quality level (95 for subtle edits, 70 for web/compressed images)
    :return: PIL Image object containing the high-contrast error map
    """
    # Open the target image and force it into standard RGB mode
    original = Image.open(image_path).convert('RGB')
    temp_jpeg = "temp_compression_test.jpg"
    
    try:
        # Step 1: Resave at target quality level to force compression divergence
        original.save(temp_jpeg, 'JPEG', quality=quality)
        compressed = Image.open(temp_jpeg)
        
        # Step 2: Determine pixel differences between original and compressed copy
        diff = ImageChops.difference(original, compressed)
        
        # Step 3: Find the maximum pixel difference to calculate a brightness scale factor
        extrema = diff.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        if max_diff == 0:
            max_diff = 1
        scale = 255.0 / max_diff
        
        # Step 4: Multiply the pixels by the scale to boost contrast and make it visible
        ela_image = diff.point(lambda p: p * int(scale))
        return ela_image

    finally:
        # Step 5: Housekeeping - Always delete the temporary file from your drive
        if os.path.exists(temp_jpeg):
            os.remove(temp_jpeg)


if __name__ == "__main__":
    # --- CONFIGURATION ---
    # Change these paths to match files on your own computer!
    input_image_path = r"E:\CV\data\r.jpg"
    output_directory = r"E:\CV\data"
    
    print("--- Processing Document Integrity (ELA) ---")
    
    try:
        # Ensure the output directory exists before saving files to it
        os.makedirs(output_directory, exist_ok=True)
        
        # Run the forensic loop at two analytical quality thresholds
        for q in [95, 70]:
            # Run the ELA analysis function
            ela_result = generate_ela(input_image_path, quality=q)
            
            # Construct the dynamic output file path
            output_file_name = f"document_ela_{q}.png"
            output_file_path = os.path.join(output_directory, output_file_name)
            
            # Save the resulting error map to disk
            ela_result.save(output_file_path)
            print(f"[Success] Generated ELA Map (Quality {q}%) -> {output_file_path}")
            
        print("\n[Analysis Complete] Open your output images to check for bright, tampered hotspots.")
        
    except FileNotFoundError:
        print(f"\n[Error] Could not find your input image at: {input_image_path}")
        print("Please double-check your 'input_image_path' variable configuration.")
        
    except Exception as e:
        print(f"\n[Unexpected Error Occurred]: {e}")
