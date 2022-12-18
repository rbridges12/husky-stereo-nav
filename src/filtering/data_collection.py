import numpy as np
import cv2
import matplotlib.pyplot as plt
from ref_histogram import segment_ref_hist_hsi
from rgb_dist import segment_rgb_dist


def make_masks():
    folder = "test_data"
    # names = ["roof_raw1", "roof_raw2", "roof_raw3", "roof_raw4"]
    name = "roof_raw"
    size = 12
    # for n in names:
    for i in range(1, size + 1):
        # BGR image
        labeled_img = cv2.imread(f"{folder}/{name}{i}_label.png")
        # floor is labeled green
        floor_mask = labeled_img[:, :, 1].astype(np.uint8)
        # hose is labeled red
        hose_mask = labeled_img[:, :, 2].astype(np.uint8)
        cv2.imshow("floor", hose_mask)
        cv2.waitKey(0)
        cv2.imwrite(f"{folder}/{name}{i}_floor.png", floor_mask)
        cv2.imwrite(f"{folder}/{name}{i}_hose.png", hose_mask)

def get_dataset():
    folder = "test_data"
    # names = ["roof_raw1", "roof_raw2", "roof_raw3", "roof_raw4"]
    name = "roof_raw"
    size = 12
    data = []
    for i in range(1, size + 1):
        img = cv2.imread(f"{folder}/{name}{i}.png")
        floor_img = cv2.imread(f"{folder}/{name}{i}_floor.png")
        hose_img = cv2.imread(f"{folder}/{name}{i}_hose.png")
        hose_img = cv2.cvtColor(hose_img, cv2.COLOR_BGR2GRAY)
        floor_img = cv2.cvtColor(floor_img, cv2.COLOR_BGR2GRAY)
        data.append((img, floor_img, hose_img))
    return data

def hsi_data_collection():
    # [(img, floor_mask), ...]
    dataset = get_dataset()

    # [(obstacle_rate, floor_rate), ...]
    obs_rates = []
    floor_rates = []

    for img, floor_mask, hose_mask in dataset:
        # print(hose_mask.shape, hose_mask)
        obstacle_mask = np.logical_not(floor_mask)
        hist_obstacle_mask = segment_ref_hist_hsi(img, floor_mask.astype(bool))
        hist_floor_mask = np.logical_not(hist_obstacle_mask)

        # show images
        obstacle_img = cv2.cvtColor(obstacle_mask.astype(np.uint8) * 255, cv2.COLOR_GRAY2BGR)
        hose_img = cv2.cvtColor(hose_mask, cv2.COLOR_GRAY2BGR)
        # cv2.imshow("test", hose_img)
        # cv2.waitKey(0)
        hist_obstacle_img = cv2.cvtColor(hist_obstacle_mask.astype(np.uint8) * 255, cv2.COLOR_GRAY2BGR)
        combined = np.vstack((np.hstack((img, hist_obstacle_img)),
                              np.hstack((obstacle_img, hose_img))))
        # cv2.imshow("combined", combined)
        # cv2.waitKey(0)

        # compute accuracy data
        # obstacle_rate = np.count_nonzero(hist_obstacle_mask & obstacle_mask) / np.count_nonzero(obstacle_mask)
        # hist_obstacle_mask = np.zeros(hist_obstacle_mask.shape).astype(bool)
        # hist_floor_mask = np.logical_not(hist_obstacle_mask)
        obstacle_rate = np.count_nonzero(hist_obstacle_mask & hose_mask) / np.count_nonzero(hose_mask)
        floor_rate = np.count_nonzero(hist_floor_mask & floor_mask) / np.count_nonzero(floor_mask)
        # accuracy_rates.append((obstacle_rate, floor_rate))
        obs_rates.append(obstacle_rate)
        floor_rates.append(floor_rate)
        print(obstacle_rate, floor_rate)
    
    obs_rates = np.array(obs_rates)
    floor_rates = np.array(floor_rates)
    # floor_rates = np.array(floor_rates)

    print(f"avg floor rate: {np.mean(floor_rates)}")
    print(f"avg obs rate: {np.mean(obs_rates)}")

    f, axs = plt.subplots(1, 2, sharey=True)
    plt.suptitle("Segmentation Accuracy of HSI Histogram Method")
    axs[0].boxplot(obs_rates, vert=True)
    axs[0].set_ylabel("% hose pixels correctly segmented")
    axs[1].boxplot(floor_rates, vert=True)
    axs[1].set_ylabel("% ground pixels correctly segmented")
    plt.show()
    
def rgb_dist_collection():
    # [(img, floor_mask), ...]
    dataset = get_dataset()

    # [(obstacle_rate, floor_rate), ...]
    obs_rates = []
    floor_rates = []

    for img, floor_mask, hose_mask in dataset:
        # print(hose_mask.shape, hose_mask)
        obstacle_mask = np.logical_not(floor_mask)
        hist_obstacle_mask = segment_rgb_dist(img)
        hist_floor_mask = np.logical_not(hist_obstacle_mask)

        # show images
        obstacle_img = cv2.cvtColor(obstacle_mask.astype(np.uint8) * 255, cv2.COLOR_GRAY2BGR)
        hose_img = cv2.cvtColor(hose_mask, cv2.COLOR_GRAY2BGR)
        # cv2.imshow("test", hose_img)
        # cv2.waitKey(0)
        hist_obstacle_img = cv2.cvtColor(hist_obstacle_mask.astype(np.uint8) * 255, cv2.COLOR_GRAY2BGR)
        combined = np.vstack((np.hstack((img, hist_obstacle_img)),
                              np.hstack((obstacle_img, hose_img))))
        # cv2.imshow("combined", combined)
        # cv2.waitKey(0)

        # compute accuracy data
        # obstacle_rate = np.count_nonzero(hist_obstacle_mask & obstacle_mask) / np.count_nonzero(obstacle_mask)
        # hist_obstacle_mask = np.zeros(hist_obstacle_mask.shape).astype(bool)
        # hist_floor_mask = np.logical_not(hist_obstacle_mask)
        obstacle_rate = np.count_nonzero(hist_obstacle_mask & hose_mask) / np.count_nonzero(hose_mask)
        floor_rate = np.count_nonzero(hist_floor_mask & floor_mask) / np.count_nonzero(floor_mask)
        # accuracy_rates.append((obstacle_rate, floor_rate))
        obs_rates.append(obstacle_rate)
        floor_rates.append(floor_rate)
        print(f"obs = {obstacle_rate:.3f}, floor = {floor_rate:.3f}")
    
    obs_rates = np.array(obs_rates)
    floor_rates = np.array(floor_rates)
    
    print(f"avg obs rate: {np.mean(obs_rates)}")
    print(f"avg floor rate: {np.mean(floor_rates)}")

    f, axs = plt.subplots(1, 2, sharey=True)
    plt.suptitle("Segmentation Accuracy of HSI Histogram Method")
    axs[0].boxplot(obs_rates, vert=True)
    axs[0].set_ylabel("% hose pixels correctly segmented")
    axs[1].boxplot(floor_rates, vert=True)
    axs[1].set_ylabel("% ground pixels correctly segmented")
    plt.show()

if __name__ == "__main__":
    print("HSI")
    hsi_data_collection()
    print("\n\n\nRGB")
    rgb_dist_collection()
    # make_masks()