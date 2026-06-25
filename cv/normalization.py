import cv2
import numpy as np
from PIL import Image

def normalize_and_save_npy(image_path, output_path, target_size=(224, 224)):
    """
    Normalize image to 224x224 and save as .npy file
    """
    # Read and resize image
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img, target_size, interpolation=cv2.INTER_LINEAR)
    
    # Normalize to [0, 1]
    img_normalized = img_resized.astype(np.float32) / 255.0
    
    # Save as .npy
    np.save(output_path, img_normalized)
    print(f"Saved normalized image to {output_path}")
    print(f"Shape: {img_normalized.shape}")
    print(f"Data type: {img_normalized.dtype}")
    print(f"Value range: [{img_normalized.min():.3f}, {img_normalized.max():.3f}]")
    
    return img_normalized


# img_array = normalize_and_save_npy('image.jpg', 'normalized_image.npy')
