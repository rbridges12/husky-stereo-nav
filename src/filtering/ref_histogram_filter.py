#!/usr/bin/python3
import rospy
import numpy as np
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header
import sensor_msgs.point_cloud2 as pc2
import cv2
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from matplotlib.colors import rgb_to_hsv
import utils
from sklearn.cluster import KMeans
import plotly.graph_objects as go


class Filter:
    def __init__(self):
        self.visualize()

    def visualize(self):
        # read in and blur image
        filename = "data/new_labeled/11_1_3.png"
        # filename = "data/rgb_img_zed1.png"
        original = cv2.imread(filename)
        img = cv2.GaussianBlur(original, (5, 5), 0)

        # convert to HSI, flatten, and remove NANs
        # print(img.dtype)
        hsi_img = utils.rgb_to_hsi(img)
        # print(hsi_img.dtype)
        hsi_colors = hsi_img.reshape((-1, 3))
        # print(np.isnan(hsi_colors))
        # print(hsi_colors[hsi_colors == np.nan].shape)
        hsi_colors[np.isnan(hsi_colors)] = 0

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        rgb_colors = img.reshape((-1, 3)).astype("float64") / 255.0

        hsv_colors = rgb_to_hsv(rgb_colors)

        # get hose, floor, and other labels from labeled image
        labels = utils.load_img_labels("data/new_labeled/11_1_3_colored.png")
        # labels = utils.load_img_labels("data/labeled_hose_ground_zed.png")

        floor_hsvs = hsv_colors[labels == 1]
        floor_hsis = hsi_colors[labels == 1]

        # hose_rgbs = rgb_colors[labels == 0.5]
        # floor_rgbs = rgb_colors[labels == 1]
        # other_rgbs = rgb_colors[labels == 0]
        # hose_hsvs = hsv_colors[labels == 0.5]
        # other_hsvs = hsv_colors[labels == 0]

        # run histogram filter using reference hsvs from labeled floor
        # obstacle_labels = self.histogram_filter(hsv_colors, floor_hsvs)
        obstacle_labels = self.histogram_filter_hsi(hsi_colors, floor_hsis)

        # make obstacle pixels pink
        img = cv2.imread(filename)
        obstacle_labels = obstacle_labels.reshape((img.shape[0], img.shape[1]))
        # obstacle_labels = (labels == 0.5).reshape((img.shape[0], img.shape[1]))
        img[obstacle_labels] = np.array([255, 0, 255])
        cv2.imwrite(f"segmented_hsi_11_1_3_2.png", img)
        cv2.imshow("labeled", img)
        # cv2.imshow("original", original)
        cv2.waitKey(0)

    def histogram_filter_hsi(self, hsis, ref_hsis):
        # make histograms of H and S or H and V for ref points
        # could be a 2D histogram
        h_hist, h_bins = np.histogram(ref_hsis[:, 0], bins=20, density=True)
        s_hist, s_bins = np.histogram(ref_hsis[:, 1], bins=20, density=True)
        i_hist, i_bins = np.histogram(ref_hsis[:, 2], bins=20, density=True)

        # filter threshold out low V and S values
        valid_hues = (hsis[:, 2] > 0.1) & (hsis[:, 1] > 0.1)
        valid_sats = hsis[:, 2] > 0.1
        
        # get values of each point in image in each histogram
        # if either histogram value is too low, its an obstacle
        # if a value is outside of the range of the histogram, it's definitely an obstacle because it has zero entries 
        h_ids = np.digitize(hsis[:, 0], h_bins) - 1
        out_of_bounds_ids = (h_ids <= 0) | (h_ids >= 20)
        h_ids[out_of_bounds_ids] = 1
        s_ids = np.digitize(hsis[:, 1], s_bins) - 1
        out_of_bounds_ids = (s_ids <= 0) | (s_ids >= 20)
        s_ids[out_of_bounds_ids] = 1
        i_ids = np.digitize(hsis[:, 2], i_bins) - 1
        out_of_bounds_ids = (i_ids <= 0) | (i_ids >= 20)
        i_ids[out_of_bounds_ids] = 1

        h_obstacles = h_hist[h_ids] < 0.2
        s_obstacles = s_hist[s_ids] < 0.0
        i_obstacles = i_hist[i_ids] < 0.1

        is_obstacle = h_obstacles | s_obstacles | i_obstacles | out_of_bounds_ids
        # is_obstacle = h_obstacles | s_obstacles | out_of_bounds_ids
        # is_obstacle = (h_obstacles & valid_hues) | (s_obstacles & valid_sats) | out_of_bounds_ids
        return is_obstacle

    def histogram_filter(self, hsvs, ref_hsvs):
        # make histograms of H and S or H and V for ref points
        # could be a 2D histogram
        h_hist, h_bins = np.histogram(ref_hsvs[:, 0], bins=20, density=True)
        s_hist, s_bins = np.histogram(ref_hsvs[:, 1], bins=20, density=True)
        v_hist, v_bins = np.histogram(ref_hsvs[:, 2], bins=20, density=True)

        # filter threshold out low V and S values
        valid_hues = (hsvs[:, 2] > 0.1) & (hsvs[:, 1] > 0.1)
        valid_sats = hsvs[:, 2] > 0.1
        
        # get values of each point in image in each histogram
        # if either histogram value is too low, its an obstacle
        # if a value is outside of the range of the histogram, it's definitely an obstacle because it has zero entries 
        h_ids = np.digitize(hsvs[:, 0], h_bins) - 1
        out_of_bounds_ids = (h_ids <= 0) | (h_ids >= 20)
        h_ids[out_of_bounds_ids] = 1
        s_ids = np.digitize(hsvs[:, 1], s_bins) - 1
        out_of_bounds_ids = (s_ids <= 0) | (s_ids >= 20)
        s_ids[out_of_bounds_ids] = 1
        v_ids = np.digitize(hsvs[:, 2], v_bins) - 1
        out_of_bounds_ids = (v_ids <= 0) | (v_ids >= 20)
        v_ids[out_of_bounds_ids] = 1

        h_obstacles = h_hist[h_ids] < 0.5
        s_obstacles = s_hist[s_ids] < 0.1
        v_obstacles = v_hist[v_ids] < 0.3

        is_obstacle = h_obstacles | s_obstacles | v_obstacles | out_of_bounds_ids
        # is_obstacle = h_obstacles | s_obstacles | out_of_bounds_ids
        # is_obstacle = (h_obstacles & valid_hues) | (s_obstacles & valid_sats) | out_of_bounds_ids
        return is_obstacle
        
    def publish_pointclouds(self, pointclouds, frame_id="map"):
        for i, points in enumerate(pointclouds):
            header = Header(stamp=rospy.Time.now(), frame_id=frame_id)
            fields = [
                PointField(name="x", offset=0, datatype=7, count=1),
                PointField(name="y", offset=4, datatype=7, count=1),
                PointField(name="z", offset=8, datatype=7, count=1),
                PointField(name="r", offset=12, datatype=7, count=1),
                PointField(name="g", offset=16, datatype=7, count=1),
                PointField(name="b", offset=20, datatype=7, count=1),
            ]
            self.pc_pubs[i].publish(pc2.create_cloud(header, fields, points))


def main():
    # rospy.init_node("ref_histogram_filter")
    filter = Filter()
    # rospy.spin()


if __name__ == "__main__":
    main()
