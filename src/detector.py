import cv2
import cv2.aruco as aruco
import numpy as np
import os
import logging
import csv

# Setup logging
logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

# Constants
ARUCO_MARKER_SIZE = 0.05  # Size of the Aruco marker in meters

# Camera calibration parameters (replace with your own calibration data)
CAMERA_MATRIX = np.array([[921.170702, 0.000000, 459.904354],
                          [0.000000, 919.018377, 351.238301], [0.000000, 0.000000, 1.000000]])
DISTORTION_COEFFS = np.array([-0.033458, 0.105152, 0.001256, -0.006647, 0.000000])



def setup_paths():
    base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    video_path = os.path.join(base_dir, "TestVideos", "classVideo.mp4")
    output_video_path = os.path.join(base_dir, "Output", "output_video.mp4")
    csv_path = os.path.join(base_dir, "Output", "output_data.csv")
    logging.info("Paths setup complete.")
    return video_path, output_video_path, csv_path


def initialize_video_capture(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logging.error("Cannot open video file")
        raise IOError("Cannot open video file")
    logging.info("Video capture initialized.")
    return cap


def setup_video_writer(cap, output_video_path):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))
    logging.info("Video writer setup complete.")
    return out


def draw_annotations(frame, corners, ids, distances, yaw_angles):
    for i, corner in enumerate(corners):
        pts = corner.reshape((4, 2)).astype(np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=5)

        if ids is not None:
            text_position = (pts[3][0][0], pts[3][0][1] + 30)  # Start below the bottom-left corner
            cv2.putText(frame, f'ID: {ids[i][0]}', text_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            text_position = (pts[3][0][0], pts[3][0][1] + 60)
            cv2.putText(frame, f'Distance: {distances[i]:.2f}m', text_position, cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0), 2)
            text_position = (pts[3][0][0], pts[3][0][1] + 90)
            cv2.putText(frame, f'Yaw: {np.degrees(yaw_angles[i]):.2f} deg', text_position, cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0), 2)


def calculate_pose_and_distance(corners):
    rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(corners, ARUCO_MARKER_SIZE, CAMERA_MATRIX, DISTORTION_COEFFS)
    distance = np.linalg.norm(tvec)
    yaw_angle = np.arctan2(tvec[0][0][0], tvec[0][0][2])
    pitch_angle = np.arctan2(tvec[0][0][1], tvec[0][0][2])
    roll_angle = 0  # Roll angle is not typically determined from a single marker's pose
    return distance, yaw_angle, pitch_angle, roll_angle, tvec, rvec


def process_video(cap, out, csv_writer):
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
                logging.info(
                    f"Frame {frame_id}: Aruco ID {aruco_id[0]} detected with distance {distance} and yaw angle {yaw_angle}.")
            draw_annotations(frame, corners, ids, distances, yaw_angles)

        out.write(frame)
        frame_id += 1


def release_resources(cap, out):
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    logging.info("Resources released.")


def show_output_video(output_video_path):
    cap = cv2.VideoCapture(output_video_path)
    if not cap.isOpened():
        logging.error("Error: Could not open the output video.")
        return

    paused = False  # Flag to control the pause state

    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow('Output Video', frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):  # Press 'q' to quit the video display early
            break
        elif key == ord('p') or key == ord(' '):  # Press 'p' or 'space' to pause/resume the video display
            paused = not paused

    cap.release()
    cv2.destroyAllWindows()

def main():
    logging.info("Application started.")
    video_path, output_video_path, csv_path = setup_paths()
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
