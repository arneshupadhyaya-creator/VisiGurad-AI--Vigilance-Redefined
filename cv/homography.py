import os
import cv2
import numpy as np

# ==========================================
# Step 1: Read Template and Scanned Image
# ==========================================

# Define your paths
refFilename = "E:/CV/data/g_format.jpg"
imFilename = "E:/CV/data/g_train.jpg"

print("Reading reference image : ", refFilename)
im1 = cv2.imread(refFilename, cv2.IMREAD_COLOR)

print("Reading image to align : ", imFilename)
im2 = cv2.imread(imFilename, cv2.IMREAD_COLOR)

# Native OpenCV display for inputs
# cv2.imshow("Original Form (Template)", im1)
# cv2.imshow("Scanned Form (To Align)", im2)
# print("Press any key on the image windows to proceed...")
# cv2.waitKey(0) 

# ==========================================
# Step 2: Find keypoints in both Images
# ==========================================

# Convert images to grayscale directly from native BGR
im1_gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
im2_gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)

MAX_NUM_FEATURES = 7000
orb = cv2.ORB_create(MAX_NUM_FEATURES)
keypoints1, descriptors1 = orb.detectAndCompute(im1_gray, None)
keypoints2, descriptors2 = orb.detectAndCompute(im2_gray, None)

# Draw features
im1_display = cv2.drawKeypoints(im1, keypoints1, outImage=np.array([]), color=(0, 0, 255), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
im2_display = cv2.drawKeypoints(im2, keypoints2, outImage=np.array([]), color=(0, 0, 255), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

# cv2.imshow("Detected Keypoints - Original", im1_display)
# cv2.imshow("Detected Keypoints - Scanned", im2_display)
# cv2.waitKey(0)

# ==========================================
# Step 3: Match keypoints in the two images
# ==========================================

matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
matches = matcher.match(descriptors1, descriptors2, None)

# Safe tuple-to-list conversion for modern OpenCV versions
matches = list(matches)

# Sort matches by score
matches.sort(key=lambda x: x.distance, reverse=False)

# Keep top 5%
numGoodMatches = int(len(matches) * 0.05)
matches = matches[:numGoodMatches]

# Draw matches
im_matches = cv2.drawMatches(im1, keypoints1, im2, keypoints2, matches, None)
# cv2.imshow("Feature Matches Across Images", im_matches)
# cv2.waitKey(0)

# ==========================================
# Step 4: Find Homography
# ==========================================

points1 = np.zeros((len(matches), 2), dtype=np.float32)
points2 = np.zeros((len(matches), 2), dtype=np.float32)

for i, match in enumerate(matches):
    points1[i, :] = keypoints1[match.queryIdx].pt
    points2[i, :] = keypoints2[match.trainIdx].pt

h, mask = cv2.findHomography(points2, points1, cv2.RANSAC)

# ==========================================
# Step 5: Warp image & Save Final Output
# ==========================================

height, width, channels = im1.shape
im2_reg = cv2.warpPerspective(im2, h, (width, height))

# Show the ultimate aligned result
cv2.imshow("FINAL ALIGNED IMAGE", im2_reg)

# CREATE OUTPUT DIRECTORY AND SAVE FILE
output_dir = "E:/CV/output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)  # Automatically creates the 'output' folder if it doesn't exist

output_path = os.path.join(output_dir, "aligned_output.png")
cv2.imwrite(output_path, im2_reg)  # Saves the image to disk
print(f"\n[SUCCESS] Aligned form successfully saved to: {output_path}")

# Keep windows alive until you press any final key, then close cleanly
print("Press any key to close all windows and exit.")
cv2.waitKey(0)
cv2.destroyAllWindows()
