import cv2
import os

# 1. Set your configurations up front
image_path = "E:/CV/data/blur_test.png"
threshold = #800

# 2. Load the image
img = cv2.imread(image_path)
if img is None:
    print(f"Error: Could not open or find the image at: {image_path}")
    exit()

# 3. Convert to grayscale (edges don't need color data)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 4. Apply the Laplacian filter to calculate edge gradients
laplacian_gradient = cv2.Laplacian(gray, cv2.CV_64F)

# 5. Calculate the variance (spread) of those edges
blur_score = laplacian_gradient.var()

print(blur_score)

# # 6. Check the score against your threshold to get the verdict
# if blur_score < threshold:
#     verdict = "BLURRY"
# else:
#     verdict = "SHARP"

# # 7. Print the results


# print(f"Calculated Blur Score : {blur_score:.2f}")
# print(f"Configured Threshold  : {threshold}")
# print(f"Verdict               : {verdict}")
