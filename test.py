# All other necessary modules
import matplotlib
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import cv2
import glob2

# Scipy image reading function
from scipy import misc

# Import local functions
from spatial_color_features import *
from hog_features import *
from sliding_window import *
from extract_features import *
from apply_heat import *
from hog_subsample import *
from classify_images import *

# Import movie editor files
from moviepy.editor import VideoFileClip

# Using this for better control over plt.show() images on Mac
matplotlib.use('TKAgg')

# Dictionary for all the parameters which can be tuned/changed
global parameter_tuning_dict
parameter_tuning_dict = {
    'color_space' : 'Lab', # Can be RGB, HSV, LUV, HLS, YUV, YCrCb
    'orient' : 9, # HOG orientations
    'pix_per_cell' : 8, # HOG pixels per cell
    'cell_per_block' : 2, # HOG cells per block
    'hog_channel' : "ALL", # Can be 0, 1, 2, or "ALL"
    'spatial_size' : (32, 32), # Spatial binning dimensions
    'hist_bins' : 32, # Number of histogram bins
    'spatial_feat' : True, # Spatial features on or off
    'hist_feat' : True, # Histogram features on or off
    'hog_feat' : True, # HOG features on or off
}

def pipelineVideo(image):
    # The following are global variables which are defined in the caller
    global box_list
    global list_of_box_list
    global detected_fifo_threshold_count
    global detected_fifo_threshold

    # Call function which classifies images and returns the model and the
    # scaler object fit for car and not-car images
    svc, X_scaler = classify_images(parameter_tuning_dict)

    # Copy of the image to draw on
    draw_image = np.copy(image)

    # To display boxes for debug
    display_boxes = False

    # The area in focus
    ystart = 400
    ystop = 656

    #scales = [0.75, 1.0]
    scales = [1.0]

    for scale in scales:
        detected_windows = find_cars(image, ystart, ystop, scale,
                                     svc, X_scaler, parameter_tuning_dict)
        if detected_windows:
            # Stack the windows detected
            if box_list == None:
                # This is the first detected window build up the FIFO
                box_list = detected_windows
                list_of_box_list.append(detected_windows)
            else:
                # FIFO threshold hasn't been reached yet, add the detected
                # windows to the FIFO
                if detected_fifo_threshold_count < detected_fifo_threshold:
                    box_list.extend(detected_windows)
                    list_of_box_list.append(detected_windows)
                else:
                    # Threshold is reached, if so then remove the oldest
                    # set of entries in the FIFO and then add the newest entry
                    oldest_box_list = list_of_box_list.pop(-1)
                    box_list.pop(len(oldest_box_list))

                    # Add the newest set of boxes detected to both lists
                    box_list.extend(detected_windows)
                    list_of_box_list.append(detected_windows)

                if display_boxes == True:
                    window_img = draw_boxes(draw_image, detected_windows,
                                            color=(0, 0, 255), thick=6)

                    plt.imshow(window_img)
                    plt.show()

            # Increment the count
            detected_fifo_threshold_count = detected_fifo_threshold_count + 1


    # Threshold has been reached, use the existing list of boxes, create a
    # heat map and then add windows around the vehicles
    if detected_fifo_threshold_count >= detected_fifo_threshold:
        # Image for adding heat(use the last image)
        heat = np.zeros_like(image[:,:,0]).astype(np.float)

        # Add heat to each box in box list
        heat = add_heat(heat, box_list)

        # Apply threshold to help remove false positives
        heat = apply_threshold(heat, 10)

        # Visualize the heatmap when displaying
        # NOTE: Limit the values from 0<->255
        heatmap = np.clip(heat, 0, 255)

        # Find final boxes from heatmap using label function
        labels = label(heatmap)
        draw_image = draw_labeled_bboxes(np.copy(image), labels)

        if display_boxes == True:
            fig = plt.figure()
            plt.subplot(121)
            plt.imshow(heatmap, cmap='hot')
            plt.title('Heat Map')
            plt.subplot(122)
            plt.imshow(draw_image)
            plt.title('Car Positions')
            fig.tight_layout()
            plt.show()

    # Return the original image if no detections were found or the modified
    # image with boxes around the vehicles(based on the heat map)
    return draw_image

# Selects which path to run
debugRun = 1

# Heat Map based on limit HOG search of the video
if debugRun == 1:
    # Call function which classifies images and returns the model and the
    # scaler object fit for car and not-car images
    svc, X_scaler = classify_images(parameter_tuning_dict)

    # List of boxe
    box_list = None
    list_of_box_list = []

    # Counter for counting FIFO
    detected_fifo_threshold_count = 0

    # Threshold for FIFO depop and repop
    detected_fifo_threshold = 3

    # Video to test on
    project_output = 'project_video_snippets/test1_output.mp4'
    project_clip = VideoFileClip("project_video_snippets/test1.mp4")
    project_clip = project_clip.fl_image(pipelineVideo)
    project_clip.write_videofile(project_output, audio=False)

    project_output = 'project_video_snippets/test2_output.mp4'
    project_clip = VideoFileClip("project_video_snippets/test2.mp4")
    project_clip = project_clip.fl_image(pipelineVideo)
    project_clip.write_videofile(project_output, audio=False)

    project_output = 'project_video_snippets/test3_output.mp4'
    project_clip = VideoFileClip("project_video_snippets/test3.mp4")
    project_clip = project_clip.fl_image(pipelineVideo)
    project_clip.write_videofile(project_output, audio=False)

    project_output = 'project_video_snippets/test4_output.mp4'
    project_clip = VideoFileClip("project_video_snippets/test4.mp4")
    project_clip = project_clip.fl_image(pipelineVideo)
    project_clip.write_videofile(project_output, audio=False)

    project_output = 'project_video_snippets/test5_output.mp4'
    project_clip = VideoFileClip("project_video_snippets/test5.mp4")
    project_clip = project_clip.fl_image(pipelineVideo)
    project_clip.write_videofile(project_output, audio=False)

    '''project_output = 'project_video_output.mp4'
    project_clip = VideoFileClip("project_video.mp4")
    project_clip = project_clip.fl_image(pipelineVideo)
    project_clip.write_videofile(project_output, audio=False)'''

    '''project_output = 'test_video_output.mp4'
    project_clip = VideoFileClip("test_video.mp4")
    project_clip = project_clip.fl_image(pipelineVideo)
    project_clip.write_videofile(project_output, audio=False)'''
# Heat Map based on limit HOG search of the video frames
if debugRun == 2:
    # Call function which classifies images and returns the model and the
    # scaler object fit for car and not-car images
    svc, X_scaler = classify_images(parameter_tuning_dict)

    # List of boxes
    box_list = None
    list_of_box_list = []

    # Counter for counting FIFO
    detected_fifo_threshold_count = 0

    # Threshold for FIFO depop and repop
    detected_fifo_threshold = 3

    # Video Images
    video_files = glob2.glob("all_video_images/*.jpg")

    # Sort the files based on the number
    # i.e. strip first 19 and last 4 characters
    # Example: all_video_images/FC1.jpg
    video_files = sorted(video_files, key=lambda name: int(name[19:-4]))

    # Parse each image
    for idx, fname in enumerate(video_files):
        if idx > 180:
            # Read image
            image = misc.imread(fname)

            # Pass to the pipeline
            pipelineVideo(image)

# Heat Map based on limit HOG search of an image
if debugRun == 3:
    # Call function which classifies images and returns the model and the
    # scaler object fit for car and not-car images
    svc, X_scaler = classify_images(parameter_tuning_dict)

    # Video Images
    video_files = glob2.glob("video_images/*.jpg")
    box_list = None

    for file in video_files:
       # Read the image
       image = mpimg.imread(file)

       # Copy of the image to draw on
       draw_image = np.copy(image)

       # To display boxes for debug
       display_boxes = False

       # The area in focus
       ystart = 400
       ystop = 656

       scales = [0.75, 1.0]
       #scales = [1.0]

       for scale in scales:
           detected_windows = find_cars(image, ystart, ystop, scale,
                                        svc, X_scaler, parameter_tuning_dict)

           if display_boxes == True:
               window_img = draw_boxes(draw_image, detected_windows,
                                       color=(0, 0, 255), thick=6)

               plt.imshow(window_img)
               plt.title("File: " + str(file) + " Scale: " + str(scale))
               plt.show()

           # Stack the hot windows verically
           if box_list == None:
               box_list = detected_windows
           else:
               box_list.extend(detected_windows)

    # Video Images
    video_files = glob2.glob("video_images/*.jpg")

    for file in video_files:
        # Image for adding heat(use the last image)
        heat = np.zeros_like(image[:,:,0]).astype(np.float)

        # Add heat to each box in box list
        heat = add_heat(heat, box_list)

        # Apply threshold to help remove false positives
        heat = apply_threshold(heat, 7)

        # Visualize the heatmap when displaying
        # NOTE: Limit the values from 0<->255
        heatmap = np.clip(heat, 0, 255)

        # Find final boxes from heatmap using label function
        labels = label(heatmap)
        draw_image = draw_labeled_bboxes(np.copy(image), labels)

        fig = plt.figure()
        plt.subplot(121)
        plt.imshow(heatmap, cmap='hot')
        plt.title('Heat Map')
        plt.subplot(122)
        plt.imshow(draw_image)
        plt.title('Car Positions of: ' + str(file))
        fig.tight_layout()
        plt.show()
# Heat Map based on HOG seach of the entire image
if debugRun == 4:
    # Video Images
    video_files = glob2.glob("video_images/*.jpg")
    box_list = None

    for file in video_files:
       # Read the image
       image = misc.imread(file)

       # Make a copy of the image
       draw_image = np.copy(image)

       # Min and max in y to search in slide_window()
       y_start_stop = [300, 700]

       # List of window sizes(definitely play around with the sizes)
       window_sizes = [32, 48, 64, 72, 96]
       #window_sizes = [32]

       for size in window_sizes:
           #print("Window Size: ", size)

           windows = slide_window(image, x_start_stop=[None, None], y_start_stop=y_start_stop,
                                  xy_window=(size, size), xy_overlap=(0.5, 0.5))

           hot_windows = search_windows(image, windows, svc, X_scaler, parameter_tuning_dict)

           '''window_img = draw_boxes(draw_image, hot_windows, color=(0, 0, 255), thick=6)

           plt.imshow(window_img)
           plt.title("Windows detected")
           plt.show()'''

           # Stack the hot windows verically
           if box_list == None:
               box_list = hot_windows
           else:
               box_list.extend(hot_windows)

    # Image for adding heat
    heat = np.zeros_like(image[:,:,0]).astype(np.float)

    # Add heat to each box in box list
    heat = add_heat(heat, box_list)

    # Apply threshold to help remove false positives
    heat = apply_threshold(heat, 7)

    # Visualize the heatmap when displaying
    # NOTE: Limit the values from 0<->255
    heatmap = np.clip(heat, 0, 255)

    # Find final boxes from heatmap using label function
    labels = label(heatmap)
    draw_image = draw_labeled_bboxes(np.copy(image), labels)

    fig = plt.figure()
    plt.subplot(121)
    plt.imshow(heatmap, cmap='hot')
    plt.title('Heat Map')
    plt.subplot(122)
    plt.imshow(draw_image)
    plt.title('Car Positions')
    plt.show()
