# All other necessary modules
import matplotlib.pyplot as plt
import numpy as np
import cv2
import glob2
import time
import os

# scikit learn modules
from sklearn.svm import LinearSVC
from sklearn.preprocessing import StandardScaler
from skimage.feature import hog
from sklearn.model_selection import train_test_split

# Scipy image reading function
from scipy import misc

# Import local functions
from spatial_color_features import *
from hog_features import *
from sliding_window import *
from extract_features import *

cars = []
notcars = []

# Read in cars and notcars
'''images = glob2.glob('labelled_data/*.jpeg')
for image in images:
    if 'image' in image or 'extra' in image:
        notcars.append(image)
    else:
        cars.append(image)'''

# Using glob2's glob API read all the images of
# vehicles and non-vehicles
car_images = glob2.glob('Datasets/vehicles/**/*.png')
for car_image in car_images:
    cars.append(car_image)

not_car_images = glob2.glob('Datasets/non-vehicles/**/*.png')
for not_car_image in not_car_images:
    notcars.append(not_car_image)

# Limit the number of images to 500
'''sample_size = 500
cars = cars[0:sample_size]
notcars = notcars[0:sample_size]'''

# Dictionary for all the parameters which can be tuned/changed
parameter_tuning_dict = {
    'color_space' : 'Lab', # Can be RGB, HSV, LUV, HLS, YUV, YCrCb
    'orient' : 9, # HOG orientations
    'pix_per_cell' : 8, # HOG pixels per cell
    'cell_per_block' : 2, # HOG cells per block
    'hog_channel' : "ALL", # Can be 0, 1, 2, or "ALL"
    'spatial_size' : (8, 8), # Spatial binning dimensions
    'hist_bins' : 16, # Number of histogram bins
    'spatial_feat' : True, # Spatial features on or off
    'hist_feat' : True, # Histogram features on or off
    'hog_feat' : True, # HOG features on or off
}

# Min and max in y to search in slide_window()
y_start_stop = [480, 700]

# Extract features of car and not-car images
car_features = extract_features(cars, parameter_tuning_dict)
notcar_features = extract_features(notcars, parameter_tuning_dict)

# Vertically stack all the features to for X(independent dataset)
X = np.vstack((car_features, notcar_features)).astype(np.float64)
# Fit a per-column scaler
X_scaler = StandardScaler().fit(X)
# Apply the scaler to X
scaled_X = X_scaler.transform(X)

# Define the labels vector
y = np.hstack((np.ones(len(car_features)), np.zeros(len(notcar_features))))

# Split up data into randomized training and test sets
#rand_state = np.random.randint(0, 100)
rand_state = 42
X_train, X_test, y_train, y_test = train_test_split(
    scaled_X, y, test_size=0.2, random_state=rand_state)

print('Using:',
      parameter_tuning_dict['color_space'], 'color space',
      parameter_tuning_dict['orient'], 'orientations',
      parameter_tuning_dict['pix_per_cell'], 'pixels per cell and',
      parameter_tuning_dict['cell_per_block'], 'cells per block')
print('Feature vector length:', len(X_train[0]))

# Use a linear SVC
svc = LinearSVC()

# Check the training time for the SVC
t1 = time.time()
svc.fit(X_train, y_train)
t2 = time.time()
print(round(t2-t1, 2), 'Seconds to train SVC...')

# Check the score of the SVC
print('Test Accuracy of SVC = ', round(svc.score(X_test, y_test), 4))

# Test the detection on a sample image
file = 'test_images/bbox-example-image.jpg'
image = misc.imread(file)
plt.imshow(image)
plt.title("Original Image")
plt.show()

# Make a copy of the image
draw_image = np.copy(image)

# List of window sizes(definitely play around with the sizes)
window_sizes = [32, 48, 64, 72, 96]

for size in window_sizes:
    print("Window Size: ", size)

    windows = slide_window(image, x_start_stop=[None, None], y_start_stop=y_start_stop,
                           xy_window=(size, size), xy_overlap=(0.5, 0.5))

    hot_windows = search_windows(image, windows, svc, X_scaler, parameter_tuning_dict)

    window_img = draw_boxes(draw_image, hot_windows, color=(0, 0, 255), thick=6)

    plt.imshow(window_img)
    plt.show()