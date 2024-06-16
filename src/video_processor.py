import cv2
from qr_code_detection import QRCodeDetector
from logger import Logger
from safe_thread import SafeThread
from file_video_stream import FileVideoStream


class VideoProcessor:
    def __init__(self, input_video_path, output_video_path, csv_path):
        self.video_stream = FileVideoStream(input_video_path)
        self.output_path = output_video_path
        self.logger = Logger(csv_path)
        self.detector = QRCodeDetector()
        self.writer = None
        self.processing_thread = None
        self.paused = False
        self.started = False

    def setup_writer(self):
        width = int(self.video_stream.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.video_stream.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self.video_stream.capture.get(cv2.CAP_PROP_FPS)
        print(f"Setting up VideoWriter with width={width}, height={height}, fps={fps}")
        self.writer = cv2.VideoWriter(self.output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
        if not self.writer.isOpened():
            print("Error: VideoWriter not opened.")
            self.writer = None

    def process_video(self):
        if not self.started:
            return

        if self.writer is None:
            self.setup_writer()
            if self.writer is None:
                print("Error: VideoWriter not initialized properly.")
                return

        while not self.processing_thread.stop_ev.is_set():
            if not self.paused and self.video_stream.more():
                ret, frame = self.video_stream.read()
                if not ret:
                    break
                detections = self.detector.detect_qr(frame)
                frame = self.detector.draw_detections(frame, detections)
                self.logger.log(self.video_stream.capture.get(cv2.CAP_PROP_POS_FRAMES), detections)
                self.writer.write(frame)
                self.display_frame(frame)

    def start_processing(self):
        self.started = True
        self.video_stream.start()
        self.processing_thread = SafeThread(self.process_video)
        self.processing_thread.start()

    def stop_processing(self):
        if self.processing_thread:
            self.processing_thread.stop()
            self.processing_thread.join()
        self.video_stream.stop()
        if self.writer is not None:
            self.writer.release()
        self.logger.save()

    def toggle_pause(self):
        self.paused = not self.paused

    def display_frame(self, frame):
        cv2.imshow("Video", frame)
        cv2.waitKey(1)

    def __del__(self):
        self.stop_processing()
