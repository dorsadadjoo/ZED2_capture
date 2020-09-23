import sys
import pyzed.sl as sl
from signal import signal, SIGINT
import cv2
import os
import pandas as pd

## 
# Basic class to handle the timestamp of the different sensors to know if it is a new sensors_data or an old one
class TimestampHandler:
    def __init__(self):
        self.t_imu = sl.Timestamp()
        self.t_baro = sl.Timestamp()
        self.t_mag = sl.Timestamp()

    ##
    # check if the new timestamp is higher than the reference one, and if yes, save the current as reference
    def is_new(self, sensor):
        if (isinstance(sensor, sl.IMUData)):
            new_ = (sensor.timestamp.get_microseconds() > self.t_imu.get_microseconds())
            if new_:
                self.t_imu = sensor.timestamp
            return new_
        elif (isinstance(sensor, sl.MagnetometerData)):
            new_ = (sensor.timestamp.get_microseconds() > self.t_mag.get_microseconds())
            if new_:
                self.t_mag = sensor.timestamp
            return new_
        elif (isinstance(sensor, sl.BarometerData)):
            new_ = (sensor.timestamp.get_microseconds() > self.t_baro.get_microseconds())
            if new_:
                self.t_baro = sensor.timestamp
            return new_

##

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
    
    # Used to store the sensors timestamp to know if the sensors_data is a new one or not
    ts_handler = TimestampHandler()
    sensors_data = sl.SensorsData()
    rows_list = []
    
    key = ' '
    while key != 113:
        if cam.grab(runtime) == sl.ERROR_CODE.SUCCESS :
            frames_recorded += 1

            # retrieve the current sensors sensors_data
            # Depending on your Camera model or its firmware, differents sensors are presents.
            # They do not run at the same rate: Therefore, to do not miss samples we iterate as fast as we can and compare timestamp to know when a sensors_data is a new one
            # NOTE: There is no need to acquire images with grab() function. Sensors sensors_data are running in a separated internal capture thread.
            if cam.get_sensors_data(sensors_data, sl.TIME_REFERENCE.CURRENT) == sl.ERROR_CODE.SUCCESS :
                # Check if the data has been updated since the last time
                # IMU is the sensor with the highest rate
                if ts_handler.is_new(sensors_data.get_imu_data()):
                    print("Sample " + str(frames_recorded))

                    print(" - IMU:")
                    # Filtered orientation quaternion
                    quaternion = sensors_data.get_imu_data().get_pose().get_orientation().get()
                    print(" \t Orientation: [ Ox: {0}, Oy: {1}, Oz {2}, Ow: {3} ]".format(quaternion[0], quaternion[1], quaternion[2], quaternion[3]))
                    
                    # linear acceleration
                    linear_acceleration = sensors_data.get_imu_data().get_linear_acceleration()
                    print(" \t Acceleration: [ {0} {1} {2} ] [m/sec^2]".format(linear_acceleration[0], linear_acceleration[1], linear_acceleration[2]))

                    # angular velocities
                    angular_velocity = sensors_data.get_imu_data().get_angular_velocity()
                    print(" \t Angular Velocities: [ {0} {1} {2} ] [deg/sec]".format(angular_velocity[0], angular_velocity[1], angular_velocity[2]))
                    
                    dict1 = {'frame':frames_recorded, 'time':sensors_data.get_imu_data().timestamp.get_microseconds(),
                    'Ox':quaternion[0] ,'Oy':quaternion[1], 'Oz':quaternion[2], 'Ow':quaternion[3],
                    'Ax':linear_acceleration[0], 'Ay':linear_acceleration[1], 'Az':linear_acceleration[2],
                    'AVx':angular_velocity[0], 'AVy':angular_velocity[1], 'AVz':angular_velocity[2]}
                    rows_list.append(dict1)

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

    df = pd.DataFrame(rows_list)
    df.to_csv(path_output[:-4]+'.csv')

    cv2.destroyAllWindows()
    cam.disable_recording()
    cam.close()

    print("\nFINISH")

if __name__ == "__main__":
    main()
