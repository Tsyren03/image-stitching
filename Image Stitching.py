import cv2
import numpy as np

def stitch_two_images(img1, img2):
    # 1. Initialize SIFT detector (Feature Points & Descriptors)
    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)

    # 2. Match features using FLANN matcher
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)

    # 3. Apply Lowe's ratio test to filter good matches
    good_matches = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good_matches.append(m)

    MIN_MATCH_COUNT = 10
    if len(good_matches) > MIN_MATCH_COUNT:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        # 4. Find Homography using RANSAC
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        # 5. Warp images to the new perspective
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]

        pts1 = np.float32([[0, 0], [0, h1], [w1, h1], [w1, 0]]).reshape(-1, 1, 2)
        pts2 = np.float32([[0, 0], [0, h2], [w2, h2], [w2, 0]]).reshape(-1, 1, 2)
        pts1_transformed = cv2.perspectiveTransform(pts1, M)
        pts = np.concatenate((pts1_transformed, pts2), axis=0)

        # Calculate dimensions for the new canvas
        [xmin, ymin] = np.int32(pts.min(axis=0).ravel() - 0.5)
        [xmax, ymax] = np.int32(pts.max(axis=0).ravel() + 0.5)

        # Translation matrix to avoid cropping negative coordinates
        t = [-xmin, -ymin]
        Ht = np.array([[1, 0, t[0]], [0, 1, t[1]], [0, 0, 1]])

        # Warp img1 and paste img2 directly (Clean overwrite, no ghosting!)
        result = cv2.warpPerspective(img1, Ht.dot(M), (xmax - xmin, ymax - ymin))
        result[t[1]:h2 + t[1], t[0]:w2 + t[0]] = img2

        return result
    else:
        print("Not enough matches are found.")
        return None

def crop_black_borders(image):
    """
    EXTRA FEATURE (5 Points): Automatically detects and cuts out the black borders
    from the stitched image to create a clean, rectangular panorama.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        return image[y:y + h, x:x + w]
    return image

if __name__ == "__main__":
    # Load 3 overlapping images
    img_left = cv2.imread('img1.jpg')
    img_center = cv2.imread('img2.jpg')
    img_right = cv2.imread('img3.jpg')

    if img_left is None or img_center is None or img_right is None:
        print("Error: Could not load one or more images. Check filenames.")
    else:
        # Step 1: Stitch Left and Center images
        print("Stitching left and center images...")
        stitched_left_center = stitch_two_images(img_left, img_center)

        # Step 2: Stitch the result with the Right image
        print("Stitching result with the right image...")
        raw_final_stitched = stitch_two_images(img_right, stitched_left_center)

        if raw_final_stitched is not None:
            # Step 3: Apply Auto-Cropping (Extra Feature)
            print("Applying Extra Feature: Cutting black borders...")
            final_clean_panorama = crop_black_borders(raw_final_stitched)

            # Save the final, clean output
            cv2.imwrite('final_panorama.jpg', final_clean_panorama)
            print("Success! Saved as final_panorama.jpg")