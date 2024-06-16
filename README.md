
# Video Processing with Aruco Markers

This project processes a video file to detect Aruco markers and annotates the video with relevant data for each identified marker. It outputs a new video with the annotations and a CSV file containing detailed information about the markers.

## Features

- Detects Aruco markers in the input video.
- Annotates each detected marker with:
  1. The QR number.
  2. The distance from the QR to the camera.
  3. The angle (yaw) that the QR is from the camera.
  4. Colors the QR perimeter green.
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

1. Place your input video file (`classVideo.mp4`) in the `TestVideos` directory.
2. Run the Python script:

```sh
python detector.py
```

3. The output video will be saved in the `Output` directory as `output_video.mp4`.
4. The output CSV file will be saved in the `Output` directory as `output_data.csv`.

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
├── Output/               # Output video and CSV file will be saved here
│
├── src/
│   └── detector.py       # The main script
│   └── README.md         # Project README file
```




## License

This project is licensed under the MIT License - see the LICENSE file for details.


## Authors

- Roni Michaeli & Elor Israeli