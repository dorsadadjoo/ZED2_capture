import sys
import pyzed.sl as sl
from signal import signal, SIGINT
import cv2
import os

cam = sl.Camera()

def handler(signal_received, frame):
    cv2.destroyAllWindows()
    cam.disable_recording()
    cam.close()
    sys.exit(0)

signal(SIGINT, handler)

def main():
    if not sys.argv or len(sys.argv) != 2:
        print("Only the path of the output SVO file should be passed as argument.")
        exit(1)
    path = 'svo_recordings/'
    try:
        os.makedirs(path)
    except FileExistsError:
        # directory already exists
        pass

    init = sl.InitParameters()
    init.camera_resolution = sl.RESOLUTION.HD720
    init.depth_mode = sl.DEPTH_MODE.PERFORMANCE
    init.coordinate_units = sl.UNIT.MILLIMETER


    status = cam.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit(1)

    path_output = path + sys.argv[1]
    recording_param = sl.RecordingParameters(path_output, sl.SVO_COMPRESSION_MODE.H264)
    err = cam.enable_recording(recording_param)
    if err != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit(1)

    runtime = sl.RuntimeParameters()
    runtime.sensing_mode = sl.SENSING_MODE.FILL
    print("SVO is Recording, use Ctrl-C to stop.")
    frames_recorded = 0
    
    # Declare your sl.Mat matrices
    image_size = cam.get_camera_information().camera_resolution
    image_size.width = image_size.width /2
    image_size.height = image_size.height /2
    image_zed = sl.Mat(image_size.width, image_size.height, sl.MAT_TYPE.U8_C4)
    depth_image_zed = sl.Mat(image_size.width, image_size.height, sl.MAT_TYPE.U8_C4)
    
    key = ' '
    while key != 113:
        if cam.grab(runtime) == sl.ERROR_CODE.SUCCESS :
            frames_recorded += 1
            cam.retrieve_image(image_zed, sl.VIEW.LEFT, sl.MEM.CPU, image_size)
            cam.retrieve_image(depth_image_zed, sl.VIEW.DEPTH, sl.MEM.CPU, image_size)
            # To recover data from sl.Mat to use it with opencv, use the get_data() method
            # It returns a numpy array that can be used as a matrix with opencv
            image_ocv = image_zed.get_data()
            depth_image_ocv = depth_image_zed.get_data()

            cv2.imshow("Image", image_ocv)
            cv2.imshow("Depth", depth_image_ocv)

            key = cv2.waitKey(1)
            print("Frame count: " + str(frames_recorded), end="\r")
    cv2.destroyAllWindows()
    cam.disable_recording()
    cam.close()

    print("\nFINISH")

if __name__ == "__main__":
    main()