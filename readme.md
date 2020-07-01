# Capture and Record using ZED2

These scripts let you capture and record single and continuous frames and their corresponding depth data using ZED2 camera.


### Prerequisites
- Windows 7 64bits or later, Ubuntu 16.04 or 18.04
- [ZED SDK](https://www.stereolabs.com/developers/) and its dependencies ([CUDA](https://developer.nvidia.com/cuda-downloads), [OpenCV](https://github.com/opencv/opencv/releases))
- [ZED Python API](https://github.com/stereolabs/zed-python-api), check the README of the github to know how to install it

## Single Frame

Open a terminal and execute the zed_single_shot.py script.


```
python3 zed_single_shot.py 
```

Two windows will pop up which show RGB and Depth data in realtime. 

Then Press 's' to save Left and Right RGBs, Depth, Depth Visualization and Point cloud.

The code automatically creates 3 directories (RGB, Depth, and Point Cloud) and saves each file in its own directory. 

You can close and re-run this script at any time. It won't overwrite existing files.


## Continuous Frames

Open a terminal and execute the svo_recording.py script and feed a name for the file to be recorded.


```
python3 svo_recording.py [file_name.svo]
```

It starts recording RGB and Depth videos in an SVO format. Press 'q' to exit.

The code automatically creates the svo_recordings directory and saves the recordings there.
Be careful about the file names, you may overwrite an existing file with the same name.

### Video Playback (Optional)

To playback the recorded videos you can run the svo_playback.py and feed the recorded file's name and address. 


```
python3 svo_playback.py ./svo_recordings/[file_name.svo]
```
Press 'q' to exit. 
