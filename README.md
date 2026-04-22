# Panoramic Image Stitcher

## Overview
This repository contains a custom implementation of an image stitching pipeline using OpenCV and Python. It automatically aligns and stitches 3 or more overlapping images into a single panoramic view. 

To comply with the assignment requirements, this program is **implemented from scratch** using classical computer vision techniques and explicitly avoids using high-level APIs like `cv2.Stitcher`.

## Implementation Details
The stitching process follows these core steps:
1. **Feature Detection & Description:** Uses the `SIFT` (Scale-Invariant Feature Transform) algorithm to extract keypoints and local descriptors from the input images.
2. **Feature Matching:** Uses the `FLANN` based matcher alongside Lowe’s ratio test to find robust correspondences between image pairs.
3. **Homography Estimation:** Applies the `RANSAC` algorithm to reject outliers and compute the perspective transformation matrix (Homography) between the images.
4. **Warping:** Uses `cv2.warpPerspective` to project the images onto a common planar canvas.

## ✨ Extra Features<img width="1000" height="1333" alt="img2" src="https://github.com/user-attachments/assets/735e0633-bd47-41ce-ae1a-65301e2316de" />
<img width="1000" height="1333" alt="img1" src="https://github.com/user-attachments/assets/4df69ad0-ab73-47af-be4e-77a388d127a3" />

To improve the final output quality, I implemented **two custom post-processing features**:

### 1. Image Blending (Alpha Blending)
When pasting warped images together, harsh visible lines ("seams") often appear where the two images meet. To fix this, I implemented an overlapping mask detection system. Where the two images overlap, the code applies a **50/50 Alpha Blend** (`cv2.addWeighted`). This creates a smooth, seamless transition between the connected images.

### 2. Automatic Image Cutting (Auto-Cropping)
Perspective warping naturally creates irregular black backgrounds (empty space) around the stitched image. I implemented an automatic image cutting function (`crop_black_borders()`). It converts the raw stitched image to grayscale, applies binary thresholding, and uses `cv2.findContours` to detect the bounding box of the actual stitched content. It then automatically crops out the black borders, resulting in a clean, perfectly rectangular final panoramic image.

## Results & Screenshots

### 1. Input Images (3 Overlapping Views)
*(Real photos taken with overlapping regions)*

**Left View:**
<img width="1000" height="1333" alt="img2" src="https://github.com/user-attachments/assets/d8e2982a-984e-4a4f-8057-47d60d9a3be7" />
**Center View:**
<img width="1000" height="1333" alt="img1" src="https://github.com/user-attachments/assets/38c6e847-b5de-49c6-8fcd-ecbad7cf4f78" />
**Right View:**
<img width="1000" height="1333" alt="img3" src="https://github.com/user-attachments/assets/5d858c4a-82c5-4d88-b73c-3bea9d5b94ba" />

### 2. Final Output: Stitched, Blended, & Auto-Cropped Panorama
The images were successfully stitched. The seams were smoothed using alpha blending, and the irregular black borders created by perspective warping were automatically detected and removed.

<img width="4640" height="3968" alt="final_panorama" src="https://github.com/user-attachments/assets/739adaf8-3034-4ab0-b1db-d13672c7cde9" />
