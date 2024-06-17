
# Video Processing with Aruco Markers

This project processes a video file to detect Aruco markers and annotates the video with relevant data for each identified marker. It outputs a new video with the annotations and generates a CSV file containing detailed information about the markers.

## Features

- **Detection and Annotation**:
  - Detects Aruco markers in the input video.
  - Annotates each detected marker with:
    1. The QR number.
    2. The distance from the QR to the camera.
    3. The yaw angle of the QR with respect to the camera.
    4. Colors the QR perimeter green.
- **Output**:
  - Outputs a new video with the above annotations.
  - Generates a CSV file containing:
    - Frame ID
    - QR ID
    - QR 2D coordinates: [QR left-up coordinate, QR right-up coordinate, QR right-down coordinate, QR left-down]
    - QR 3D information: [distance, yaw, pitch, roll]

## Prerequisites

Ensure you have the following installed:

- Python 3.x
- OpenCV
- Numpy

Install the necessary packages using pip:

```sh
pip install opencv-python numpy
```

## Usage

1. **Prepare the Input Video**: Place your input video file (`classVideo.mp4`) in the `TestVideos` directory.
2. **Run the Script**: Execute the Python script to process the video.

```sh
python src/detector.py
```

3. **Output Files**: 
   - The processed video will be saved in the `Output` directory as `output_video.mp4`.
   - The CSV file containing detailed information will be saved in the `Output` directory as `output_data.csv`.

## Controls

- **Pause/Resume**: Press `p` or `space` to pause and resume the video playback.
- **Exit**: Press `q` to quit the video playback.
- **Step Forward**: Press `d` to move one frame forward.
- **Step Backward**: Press `a` to move one frame backward.

## Explanation of Data Processing

### Real-time Data Visualization

When the script runs, it processes each frame of the video to detect Aruco markers. For each detected marker, the following annotations are added to the frame:

1. **QR Number**: Displayed below the marker.
2. **Distance**: The distance from the marker to the camera is calculated and displayed below the QR number.
3. **Yaw Angle**: The yaw angle (orientation) of the marker relative to the camera is calculated and displayed below the distance.
4. **Green Perimeter**: The perimeter of the detected marker is colored green to highlight its position.

### Distance and Angle Calculation

- **Distance**: Calculated using the known size of the Aruco marker and the camera calibration parameters.
- **Yaw Angle**: Calculated based on the position of the marker relative to the camera.

### CSV Output

The CSV file (`output_data.csv`) contains detailed information about each detected marker:

- **Frame ID**: The frame number in which the marker was detected.
- **QR ID**: The identifier of the detected QR marker.
- **QR 2D Coordinates**: The four corner points of the marker in the frame.
- **QR 3D Information**: The distance, yaw, pitch, and roll angles of the marker relative to the camera.

### Logging

The `app.log` file provides detailed logs of the processing, including:

- Initialization messages.
- Detected markers and their corresponding data for each frame.
- Completion and resource release messages.

## Directory Structure

```
Detect_QR_on_video/
│
├── Documents/
│   └── TelloAI - Qualification stage.pdf
│
├── TestVideos/
│   └── classVideo.mp4
│
├── Output/   
│   └── output_video.mp4
│   └── output_data.csv
│   └── app.log
│
├── src/
│   └── detector.py       # The main script
│   └── README.md         # Project README file
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Authors

- Roni Michaeli 
- Elor Israeli
- Roi Asraf
- Naor Ladani
