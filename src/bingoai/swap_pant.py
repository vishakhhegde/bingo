import os
import cv2
import json

import numpy as np

from absl import app
from absl import flags
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

flags.DEFINE_string('source_image', None, 'Source image of a cloth')
flags.DEFINE_string('source_keypoints', None, 'Source keypoints')
flags.DEFINE_string('target_image', None, 'Target image of a person')
flags.DEFINE_string('target_keypoints', None, 'Target keypoints')
FLAGS = flags.FLAGS

def extract_index_nparray(nparray):
    index = None
    for num in nparray[0]:
        index = num
        break
    return index

def check_if_useful_triangle(pt1, pt2, pt3, shape_points):
    mid_point = (np.array(pt1) + np.array(pt2) + np.array(pt3))/3
    point = Point(mid_point[0], mid_point[1])
    polygon = Polygon(shape_points)
    return polygon.contains(point)

def main(argv):
    del argv
    # Read source keypoints
    with open(FLAGS.source_keypoints, 'r') as fin_s:
        source_keypoints = json.load(fin_s)
    
    # Read target keypoints
    with open(FLAGS.target_keypoints, 'r') as fin_t:
        target_keypoints = json.load(fin_t)

    # Read source image
    source_img = cv2.imread(FLAGS.source_image)
    source_img = cv2.resize(source_img, (640, 480))
    source_img_gray = cv2.cvtColor(source_img, cv2.COLOR_BGR2GRAY)
    source_mask = np.zeros_like(source_img_gray)

    # Read target image
    target_img = cv2.imread(FLAGS.target_image)
    target_img_shape = target_img.shape
    target_img = cv2.resize(target_img, (640, 480))
    target_img_gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)

    # Create empty target new image
    target_img_new = np.zeros_like(target_img, np.uint8)

    source_points = np.array(source_keypoints['keypoints'], np.int32)
    source_convexhull = cv2.convexHull(source_points)
    cv2.fillConvexPoly(source_mask, source_convexhull, 255)

    target_points = np.array(target_keypoints['keypoints'], np.int32)
    target_convexhull = cv2.convexHull(target_points)

    # Delaunay triangulation
    source_rect = cv2.boundingRect(source_convexhull)
    source_subdiv = cv2.Subdiv2D(source_rect)
    source_subdiv.insert(source_keypoints['keypoints'])
    source_triangles = source_subdiv.getTriangleList()
    source_triangles = np.array(source_triangles, dtype=np.int32)

    indexes_triangles = []
    for t in source_triangles:
        pt1 = (t[0], t[1])
        pt2 = (t[2], t[3])
        pt3 = (t[4], t[5])

        if not check_if_useful_triangle(pt1, pt2, pt3, source_points):
            continue

        index_pt1 = np.where((source_points == pt1).all(axis=1))
        index_pt1 = extract_index_nparray(index_pt1)

        index_pt2 = np.where((source_points == pt2).all(axis=1))
        index_pt2 = extract_index_nparray(index_pt2)

        index_pt3 = np.where((source_points == pt3).all(axis=1))
        index_pt3 = extract_index_nparray(index_pt3)

        if index_pt1 is not None and index_pt2 is not None and index_pt3 is not None:
            triangle = [index_pt1, index_pt2, index_pt3]
            indexes_triangles.append(triangle)

    print(len(indexes_triangles))

    for triangle_index in indexes_triangles:
        tr1_pt1 = source_keypoints['keypoints'][triangle_index[0]]
        tr1_pt2 = source_keypoints['keypoints'][triangle_index[1]]
        tr1_pt3 = source_keypoints['keypoints'][triangle_index[2]]
        triangle1 = np.array([tr1_pt1, tr1_pt2, tr1_pt3], np.int32)

        tr2_pt1 = target_keypoints['keypoints'][triangle_index[0]]
        tr2_pt2 = target_keypoints['keypoints'][triangle_index[1]]
        tr2_pt3 = target_keypoints['keypoints'][triangle_index[2]]
        triangle2 = np.array([tr2_pt1, tr2_pt2, tr2_pt3], np.int32)

        rect1 = cv2.boundingRect(triangle1)
        (x, y, w, h) = rect1
        cropped_triangle = source_img[y: y + h, x: x + w]
        cropped_tr1_mask = np.zeros((h, w), np.uint8)
        points = np.array([[tr1_pt1[0] - x, tr1_pt1[1] - y],
                           [tr1_pt2[0] - x, tr1_pt2[1] - y],
                           [tr1_pt3[0] - x, tr1_pt3[1] - y]], np.int32)
        cv2.fillConvexPoly(cropped_tr1_mask, points, 255)

        rect2 = cv2.boundingRect(triangle2)
        (x, y, w, h) = rect2
        cropped_tr2_mask = np.zeros((h, w), np.uint8)
        points2 = np.array([[tr2_pt1[0] - x, tr2_pt1[1] - y],
                            [tr2_pt2[0] - x, tr2_pt2[1] - y],
                            [tr2_pt3[0] - x, tr2_pt3[1] - y]], np.int32)
        cv2.fillConvexPoly(cropped_tr2_mask, points2, 255)

        # Warp triangles
        points = np.float32(points)
        points2 = np.float32(points2)
        M = cv2.getAffineTransform(points, points2)
        warped_triangle = cv2.warpAffine(cropped_triangle, M, (w, h))
        warped_triangle = cv2.bitwise_and(warped_triangle, warped_triangle, mask=cropped_tr2_mask)

        # Reconstructing destination face
        target_img_new_rect_area = target_img_new[y: y + h, x: x + w]
        target_img_new_rect_area_gray = cv2.cvtColor(target_img_new_rect_area, cv2.COLOR_BGR2GRAY)
        _, mask_triangles_designed = cv2.threshold(target_img_new_rect_area_gray, 1, 255, cv2.THRESH_BINARY_INV)
        warped_triangle = cv2.bitwise_and(warped_triangle, warped_triangle, mask=mask_triangles_designed)

        # Modify only the triangle in consideration
        target_img_new_rect_area = cv2.add(target_img_new_rect_area, warped_triangle)
        target_img_new[y: y + h, x: x + w] = target_img_new_rect_area

    target_img_mask_inv = np.sum(target_img_new, axis=2) > 0
    target_img_mask_inv = np.array(target_img_mask_inv.astype(int)*255, np.int8)

    target_img_mask = np.zeros_like(target_img_mask_inv)
    target_img_mask = cv2.bitwise_not(target_img_mask_inv)
    target_img_orig = cv2.bitwise_and(target_img, target_img, mask=target_img_mask)
    target_img_new_full = cv2.add(target_img_orig, target_img_new)

    target_img_new_full = cv2.resize(target_img_new_full, (target_img_shape[1], target_img_shape[0]))
    cv2.imshow('image', target_img_new_full)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    app.run(main)
