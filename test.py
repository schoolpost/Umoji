from __future__ import print_function
import cv2 as cv
import numpy as np

src = cv.imread("happy.png", cv.IMREAD_UNCHANGED)

srcTri = np.array([[0, 0], [src.shape[1] - 1, 0],
                   [0, src.shape[0] - 1]]).astype(np.float32)
dstTri = np.array([[0, src.shape[1]*0.33], [src.shape[1]*0.85, src.shape[0]
                                            * 0.25], [src.shape[1]*0.15, src.shape[0]*0.7]]).astype(np.float32)
warp_mat = cv.getAffineTransform(srcTri, dstTri)
warp_dst = cv.warpAffine(src, warp_mat, (src.shape[1], src.shape[0]))
# Rotating the image after Warp
center = (warp_dst.shape[1]//2, warp_dst.shape[0]//2)
angle = -50
scale = 0.6
rot_mat = cv.getRotationMatrix2D(center, angle, scale)
warp_rotate_dst = cv.warpAffine(
    warp_dst, rot_mat, (warp_dst.shape[1], warp_dst.shape[0]))
cv.imshow('Source image', src)
cv.imshow('Warp', warp_dst)
cv.imshow('Warp + Rotate', warp_rotate_dst)
cv.waitKey()
