import cv2
import cv2.aruco as aruco
import numpy as np
import os
import logging
import csv

# Setup logging
logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

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

def draw_green_perimeter_and_id(frame, corners, ids):
    for i, corner in enumerate(corners):
        pts = corner.reshape((4, 2)).astype(np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=5)
        if ids is not None:
            cv2.putText(frame, f'ID: {ids[i][0]}', tuple(pts[0][0]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

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
            draw_green_perimeter_and_id(frame, corners, ids)
            for aruco_id in ids:
                csv_writer.writerow([frame_id, aruco_id[0]])
                logging.info(f"Frame {frame_id}: Aruco ID {aruco_id[0]} detected.")

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

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow('Output Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit the video display early
            break

    cap.release()
    cv2.destroyAllWindows()

def main():
    logging.info("Application started.")
    video_path, output_video_path, csv_path = setup_paths()
    cap = initialize_video_capture(video_path)
    out = setup_video_writer(cap, output_video_path)

    with open(csv_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Frame ID', 'Aruco ID'])
        logging.info("CSV file initialized.")

        process_video(cap, out, csv_writer)

    logging.info("CSV file closed.")
    release_resources(cap, out)
    show_output_video(output_video_path)  # Add this to show the video

if __name__ == "__main__":
    main()
