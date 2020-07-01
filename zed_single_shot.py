import sys
import numpy as np
import pyzed.sl as sl
import cv2
import os
import glob

help_string = "[s] Save side by side image [d] Save Depth, [p] Save Point Cloud, [q] Quit"
prefix_point_cloud = "Cloud_"
prefix_depth = "Depth_"
path = "./"
rgb_path = "./rgb/"
depth_path = "./depth/"
pcl_path = "./point_cloud/"

count_save = 0
mode_point_cloud = 0
mode_depth = 0
point_cloud_format_ext = ".pcd"
depth_format_ext = ".png"

def save_point_cloud(zed, filename) :
    print("Saving Point Cloud...")
    tmp = sl.Mat()
    zed.retrieve_measure(tmp, sl.MEASURE.XYZRGBA)
    saved = (tmp.write(filename + point_cloud_format_ext) == sl.ERROR_CODE.SUCCESS)
    if saved :
        print("Done")
    else :
        print("Failed... Please check that you have permissions to write on disk")

def save_depth(zed, filename) :
    print("Saving Depth Map...")
    tmp = sl.Mat()
    zed.retrieve_measure(tmp, sl.MEASURE.DEPTH)
    saved = (tmp.write(filename + depth_format_ext) == sl.ERROR_CODE.SUCCESS)
    if saved :
        print("Done")
    else :
        print("Failed... Please check that you have permissions to write on disk")
    
    tmp = sl.Mat(mat_type=sl.MAT_TYPE.U8_C4)
    zed.retrieve_image(tmp, sl.VIEW.DEPTH, sl.MEM.CPU)
    saved = (tmp.write(filename + "_viz" + depth_format_ext) == sl.ERROR_CODE.SUCCESS)
    
def save_rgb_image(zed, filename,file_format) :

    image_sl_left = sl.Mat()
    zed.retrieve_image(image_sl_left, sl.VIEW.LEFT)
    image_cv_left = image_sl_left.get_data()

    image_sl_right = sl.Mat()
    zed.retrieve_image(image_sl_right, sl.VIEW.RIGHT)
    image_cv_right = image_sl_right.get_data()
    
    cv2.imwrite(filename + "_left" + file_format, image_cv_left)
    cv2.imwrite(filename + "_right" + file_format, image_cv_right)

def process_key_event(zed, key) :
    global mode_depth
    global mode_point_cloud
    global count_save
    global depth_format_ext
    global point_cloud_format_ext

    if key == 115:
        save_rgb_image(zed, rgb_path + str(count_save) , ".png")
        save_depth(zed, depth_path + prefix_depth + str(count_save))
        save_point_cloud(zed, pcl_path + prefix_point_cloud + str(count_save))
        count_save += 1
   
    elif key == 104 or key == 72:
        print(help_string)
    else:
        a = 0

def print_help() :
    print(" Press 's' to save RGB, Depth and Point cloud")

def check_dir():
    global count_save

    try:
        os.makedirs(rgb_path)
        os.makedirs(depth_path)
        os.makedirs(pcl_path)
    except FileExistsError:
        # directory already exists
        pass

    count_save = len(glob.glob(pcl_path+'*.pcd'))
    print(count_save)

def main() :

    # Create a ZED camera object
    zed = sl.Camera()

    # Set configuration parameters
    input_type = sl.InputType()
    if len(sys.argv) >= 2 :
        input_type.set_from_svo_file(sys.argv[1])
    init = sl.InitParameters(input_t=input_type)
    init.camera_resolution = sl.RESOLUTION.HD720
    init.depth_mode = sl.DEPTH_MODE.PERFORMANCE
    init.coordinate_units = sl.UNIT.MILLIMETER
    # init.depth_minimum_distance = 0.3

    # Open the camera
    err = zed.open(init)
    if err != sl.ERROR_CODE.SUCCESS :
        print(repr(err))
        zed.close()
        exit(1)

    # Display help in console
    print_help()
    print(count_save)
    # check for existing folders and number of previously captured frames
    check_dir()

    # Set runtime parameters after opening the camera
    runtime = sl.RuntimeParameters()
    runtime.sensing_mode = sl.SENSING_MODE.FILL

    # Prepare new image size to retrieve half-resolution images
    image_size = zed.get_camera_information().camera_resolution
    image_size.width = image_size.width /2
    image_size.height = image_size.height /2

    # Declare your sl.Mat matrices
    image_zed = sl.Mat(image_size.width, image_size.height, sl.MAT_TYPE.U8_C4)
    depth_image_zed = sl.Mat(image_size.width, image_size.height, sl.MAT_TYPE.U8_C4)
    point_cloud = sl.Mat()

    key = ' '
    while key != 113 :
        err = zed.grab(runtime)
        if err == sl.ERROR_CODE.SUCCESS :
            # Retrieve the left image, depth image in the half-resolution
            zed.retrieve_image(image_zed, sl.VIEW.LEFT, sl.MEM.CPU, image_size)
            zed.retrieve_image(depth_image_zed, sl.VIEW.DEPTH, sl.MEM.CPU, image_size)
            # Retrieve the RGBA point cloud in half resolution
            zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA, sl.MEM.CPU, image_size)

            # To recover data from sl.Mat to use it with opencv, use the get_data() method
            # It returns a numpy array that can be used as a matrix with opencv
            image_ocv = image_zed.get_data()
            depth_image_ocv = depth_image_zed.get_data()

            cv2.imshow("Image", image_ocv)
            cv2.imshow("Depth", depth_image_ocv)

            key = cv2.waitKey(10)

            process_key_event(zed, key)

    cv2.destroyAllWindows()
    zed.close()

    print("\nFINISH")

if __name__ == "__main__":
    main()
