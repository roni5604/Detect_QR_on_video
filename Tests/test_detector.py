import unittest
import cv2
import numpy as np
import os
import csv
from src import detector


class TestArucoDetection(unittest.TestCase):

    def setUp(self):
        self.video_path, self.output_video_path, self.csv_path, self.log_path = detector.setup_paths()
        self.cap = detector.initialize_video_capture(self.video_path)
        self.out = detector.setup_video_writer(self.cap, self.output_video_path)

    def tearDown(self):
        self.cap.release()
        self.out.release()

    def test_setup_paths(self):
        video_path, output_video_path, csv_path, log_path = detector.setup_paths()
        self.assertTrue(os.path.exists(video_path))
        self.assertTrue(os.path.exists(os.path.dirname(output_video_path)))
        self.assertTrue(os.path.exists(os.path.dirname(csv_path)))
        self.assertTrue(os.path.exists(os.path.dirname(log_path)))

    def test_initialize_video_capture(self):
        cap = detector.initialize_video_capture(self.video_path)
        self.assertTrue(cap.isOpened())
        cap.release()

    def test_setup_video_writer(self):
        cap = detector.initialize_video_capture(self.video_path)
        out = detector.setup_video_writer(cap, self.output_video_path)
        self.assertIsNotNone(out)
        cap.release()
        out.release()

    def test_calculate_pose_and_distance(self):
        corners = np.array([[[0, 0], [1, 0], [1, 1], [0, 1]]], dtype=np.float32)
        distance, yaw_angle, pitch_angle, roll_angle, tvec, rvec = detector.calculate_pose_and_distance(corners)

        # Ensure distance is within the expected range
        self.assertTrue(0 <= distance <= 60, f"Distance out of range: {distance}")

        # Ensure yaw angle is within the expected range
        self.assertTrue(-180 <= yaw_angle <= 180, f"Yaw angle out of range: {yaw_angle}")

        # Ensure pitch angle is within the expected range
        self.assertTrue(-180 <= pitch_angle <= 180, f"Pitch angle out of range: {pitch_angle}")

    def test_draw_annotations(self):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        corners = [np.array([[100, 100], [200, 100], [200, 200], [100, 200]], dtype=np.float32)]
        ids = np.array([[1]])
        distances = [1.0]
        yaw_angles = [0.0]
        detector.draw_annotations(frame, corners, ids, distances, yaw_angles)
        # Check if annotations were drawn
        self.assertTrue(np.any(frame[100:200, 100:200] != 0))

    def test_process_video(self):
        with open(self.csv_path, mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Frame ID', 'QR id', 'QR 2D', 'QR 3D'])
            detector.process_video(self.cap, self.out, csv_writer)

        self.assertTrue(os.path.exists(self.output_video_path))
        self.assertTrue(os.path.exists(self.csv_path))
        self.assertGreater(os.path.getsize(self.csv_path), 0)


if __name__ == '__main__':
    unittest.main()
