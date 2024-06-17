import cv2
import cv2.aruco as aruco
import numpy as np
import os
import logging
import csv

# Constants
ARUCO_MARKER_SIZE = 0.05  # Size of the Aruco marker in meters

# Camera calibration parameters for the camera used to capture the video
CAMERA_MATRIX = np.array([[921.170702, 0.000000, 459.904354],
                          [0.000000, 919.018377, 351.238301],
                          [0.000000, 0.000000, 1.000000]])
DISTORTION_COEFFS = np.array([-0.033458, 0.105152, 0.001256, -0.006647, 0.000000])

def setup_paths():
    """
    Sets up the paths for input video, output video, CSV file, and log file.

    Returns:
        tuple: Paths for input video, output video, CSV file, and log file.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    video_path = os.path.join(base_dir, "TestVideos", "classVideo.mp4")
    output_video_path = os.path.join(base_dir, "Output", "output_video.mp4")
    csv_path = os.path.join(base_dir, "Output", "output_data.csv")
    log_path = os.path.join(base_dir, "Output", "app.log")
    return video_path, output_video_path, csv_path, log_path

# Get paths and setup logging
video_path, output_video_path, csv_path, log_path = setup_paths()
logging.basicConfig(level=logging.DEBUG, filename=log_path, filemode='w', format='%(name)s - %(levelname)s - %(message)s')

def initialize_video_capture(video_path):
    """
    Initializes the video capture object.

    Args:
        video_path (str): Path to the input video file.

    Returns:
        cv2.VideoCapture: Video capture object.

    Raises:
        IOError: If the video file cannot be opened.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logging.error("Cannot open video file")
        raise IOError("Cannot open video file")
    logging.info("Video capture initialized.")
    return cap

def setup_video_writer(cap, output_video_path):
    """
    Sets up the video writer object.

    Args:
        cap (cv2.VideoCapture): Video capture object.
        output_video_path (str): Path to the output video file.

    Returns:
        cv2.VideoWriter: Video writer object.
    """
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))
    logging.info("Video writer setup complete.")
    return out

def draw_annotations(frame, corners, ids, distances, yaw_angles):
    """
    Draws annotations on the frame, including Aruco ID, distance, and yaw angle.

    Args:
        frame (np.ndarray): Frame to draw annotations on.
        corners (list): List of corners of detected Aruco markers.
        ids (list): List of IDs of detected Aruco markers.
        distances (list): List of distances to the detected Aruco markers.
        yaw_angles (list): List of yaw angles of the detected Aruco markers.
    """
    for i, corner in enumerate(corners):
        pts = corner.reshape((4, 2)).astype(np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=5)

        if ids is not None:
            text_position = (pts[3][0][0], pts[3][0][1] + 30)  # Start below the bottom-left corner
            cv2.putText(frame, f'ID: {ids[i][0]}', text_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            text_position = (pts[3][0][0], pts[3][0][1] + 60)
            cv2.putText(frame, f'Distance: {distances[i]:.2f}m', text_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            text_position = (pts[3][0][0], pts[3][0][1] + 90)
            cv2.putText(frame, f'Yaw: {yaw_angles[i]:.2f} deg', text_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

def calculate_pose_and_distance(corners):
    """
    Calculates the pose and distance of the Aruco marker.

    Args:
        corners (np.ndarray): Corners of the detected Aruco marker.

    Returns:
        tuple: Distance, yaw angle, pitch angle, roll angle, translation vector, and rotation vector.
    """
    rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(corners, ARUCO_MARKER_SIZE, CAMERA_MATRIX, DISTORTION_COEFFS)
    distance = np.linalg.norm(tvec)
    yaw_angle = np.arctan2(tvec[0][0][0], tvec[0][0][2])
    yaw_angle_degrees = np.degrees(yaw_angle)
    yaw_angle_degrees = (yaw_angle_degrees + 180) % 360 - 180  # Normalize to -180 to 180 degrees
    pitch_angle = np.degrees(np.arctan2(tvec[0][0][1], tvec[0][0][2]))
    roll_angle = 0  # Roll angle is not typically determined from a single marker's pose
    return distance, yaw_angle_degrees, pitch_angle, roll_angle, tvec, rvec

def process_video(cap, out, csv_writer):
    """
    Processes the video, detects Aruco markers, annotates frames, and writes to the output video and CSV file.

    Args:
        cap (cv2.VideoCapture): Video capture object.
        out (cv2.VideoWriter): Video writer object.
        csv_writer (csv.writer): CSV writer object.
    """
    logging.info("Processing video.")
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_100)
    parameters = aruco.DetectorParameters()
    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            logging.info("End of video file reached.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = aruco.detectMarkers(image=gray, dictionary=aruco_dict, parameters=parameters)

        if ids is not None:
            distances = []
            yaw_angles = []
            for i, aruco_id in enumerate(ids):
                distance, yaw_angle, pitch_angle, roll_angle, tvec, rvec = calculate_pose_and_distance(corners[i])
                distances.append(distance)
                yaw_angles.append(yaw_angle)
                csv_writer.writerow([frame_id, aruco_id[0],
                                     f"[{corners[i][0][0]}, {corners[i][0][1]}, {corners[i][0][2]}, {corners[i][0][3]}]",
                                     f"[{distance}, {yaw_angle}, {pitch_angle}, {roll_angle}]"])
                logging.info(f"Frame {frame_id}: Aruco ID {aruco_id[0]} detected with distance {distance} and yaw angle {yaw_angle}.")
            draw_annotations(frame, corners, ids, distances, yaw_angles)

        out.write(frame)
        frame_id += 1

def release_resources(cap, out):
    """
    Releases the resources for video capture and video writer objects.

    Args:
        cap (cv2.VideoCapture): Video capture object.
        out (cv2.VideoWriter): Video writer object.
    """
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    logging.info("Resources released.")

def show_output_video(output_video_path):
    """
    Displays the output video in real-time with controls for pausing, resuming, and stepping through frames.
    Args:
        output_video_path (str): Path to the output video file.
    """
    cap = cv2.VideoCapture(output_video_path)
    if not cap.isOpened():
        logging.error("Error: Could not open the output video.")
        return

    paused = False  # Flag to control the pause state
    delay = 33  # Initial delay for 30 fps playback (33 ms between frames)

    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                break

            # Create a black image for controls with the same width as the video frame
            controls_img = np.zeros((220, frame.shape[1], 3), dtype=np.uint8)
            cv2.putText(controls_img, "Controls", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(controls_img, "- Pause/Resume: Press 'p' or 'space'", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            cv2.putText(controls_img, "- Exit: Press 'q' or 'e'", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            cv2.putText(controls_img, "- Step Forward: Press 'd'", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            cv2.putText(controls_img, "- Step Backward: Press 'a'", (10, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

            # Combine video frame with controls image
            combined_img = np.vstack((frame, controls_img))
            cv2.imshow('Output Video', combined_img)

        key = cv2.waitKey(delay) & 0xFF

        if key == ord('q') or key == ord('e'):  # Press 'q' or 'e' to exit the video display
            break
        elif key == ord('p') or key == ord(' '):  # Press 'p' or 'space' to pause/resume the video display
            paused = not paused
        elif key == ord('d') or key == ord('D'):  # Press 'd' to step forward one frame when paused
            paused = True
            ret, frame = cap.read()
            if not ret:
                break
            controls_img = np.zeros((220, frame.shape[1], 3), dtype=np.uint8)
            cv2.putText(controls_img, "Controls", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(controls_img, "- Pause/Resume: Press 'p' or 'space'", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            cv2.putText(controls_img, "- Exit: Press 'q' or 'e'", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            cv2.putText(controls_img, "- Step Forward: Press 'd'", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            cv2.putText(controls_img, "- Step Backward: Press 'a'", (10, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            combined_img = np.vstack((frame, controls_img))
            cv2.imshow('Output Video', combined_img)
        elif key == ord('a') or key == ord('A'):  # Press 'a' to step back one frame when paused
            paused = True
            current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            cap.set(cv2.CAP_PROP_POS_FRAMES, max(current_frame - 2, 0))
            ret, frame = cap.read()
            if not ret:
                break
            controls_img = np.zeros((220, frame.shape[1], 3), dtype=np.uint8)
            cv2.putText(controls_img, "Controls", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(controls_img, "- Pause/Resume: Press 'p' or 'space'", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            cv2.putText(controls_img, "- Exit: Press 'q' or 'e'", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            cv2.putText(controls_img, "- Step Forward: Press 'd'", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            cv2.putText(controls_img, "- Step Backward: Press 'a'", (10, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            combined_img = np.vstack((frame, controls_img))
            cv2.imshow('Output Video', combined_img)

    cap.release()
    cv2.destroyAllWindows()

def main():
    """
    Main function to run the video processing and display.
    """
    logging.info("Application started.")
    video_path, output_video_path, csv_path, log_path = setup_paths()
    cap = initialize_video_capture(video_path)
    out = setup_video_writer(cap, output_video_path)

    with open(csv_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Frame ID', 'QR id', 'QR 2D', 'QR 3D'])
        logging.info("CSV file initialized.")

        process_video(cap, out, csv_writer)

    logging.info("CSV file closed.")
    release_resources(cap, out)
    show_output_video(output_video_path)  # Add this to show the video

if __name__ == "__main__":
    main()
