import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
from video_processor import VideoProcessor

class VideoApp:
    def __init__(self, video_path, output_video_path, csv_path):
        self.root = tk.Tk()
        self.root.title("QR Code Detection")
        self.video_processor = VideoProcessor(video_path, output_video_path, csv_path)

        self.video_frame = ttk.Label(self.root)
        self.video_frame.grid(row=0, column=0, columnspan=2)

        self.start_button = ttk.Button(self.root, text="Start", command=self.start_video)
        self.start_button.grid(row=1, column=0)

        self.pause_button = ttk.Button(self.root, text="Pause", command=self.pause_video)
        self.pause_button.grid(row=1, column=1)

    def start_video(self):
        self.video_processor.resume_processing()

    def pause_video(self):
        self.video_processor.pause_processing()

    def update_frame(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)
        self.video_frame.imgtk = image
        self.video_frame.configure(image=image)
        self.root.after(10, self.update_frame)

    def run(self):
        self.video_processor.display_frame = self.update_frame
        self.video_processor.start_processing()
        self.root.mainloop()
        self.video_processor.stop_processing()
